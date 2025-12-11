-- Modern LSP setup using vim.lsp.start instead of deprecated lspconfig

-- Cache for uv script python paths (filepath -> python_path)
local uv_python_cache = {}

-- Check if a buffer is a uv inline script (has --script in shebang)
local function is_uv_script(bufnr)
	local first_line = vim.api.nvim_buf_get_lines(bufnr, 0, 1, false)[1] or ""
	return first_line:match("^#!/usr/bin/env.*uv.*%-%-script") ~= nil
end

-- Async resolve uv script python path and restart LSP
local function resolve_uv_python_async(bufnr, filepath)
	if uv_python_cache[filepath] then
		return
	end

	-- Use uv sync --script to resolve env without executing the script
	vim.system(
		{ "uv", "sync", "--script", filepath },
		{ text = true },
		function(result)
			local output = (result.stdout or "") .. (result.stderr or "")
			-- Parse: "Using script environment at: /path/to/env"
			local env_path = output:match("Using script environment at: ([^\n]+)")
			if env_path then
				local python_path = env_path .. "/bin/python"
				uv_python_cache[filepath] = python_path
				-- Restart pyright with correct python path
				vim.schedule(function()
					if vim.api.nvim_buf_is_valid(bufnr) then
						for _, client in ipairs(vim.lsp.get_clients({ bufnr = bufnr, name = "pyright" })) do
							client:stop()
						end
						vim.api.nvim_exec_autocmds("FileType", { buffer = bufnr })
					end
				end)
			end
		end
	)
end

-- Get python path for a buffer (sync, uses cache)
local function get_python_path(bufnr)
	local filepath = vim.api.nvim_buf_get_name(bufnr)

	-- Check uv cache first
	if uv_python_cache[filepath] then
		return uv_python_cache[filepath]
	end

	-- Search for .venv/env directories
	local current_dir = vim.fn.expand("#" .. bufnr .. ":p:h")
	local venv_names = { ".venv", "env" }

	local function find_venv(dir)
		for _, venv_name in ipairs(venv_names) do
			local venv_python = dir .. "/" .. venv_name .. "/bin/python"
			if vim.fn.filereadable(venv_python) == 1 then
				return venv_python
			end
		end
		local parent = vim.fn.fnamemodify(dir, ":h")
		if parent ~= dir and parent ~= "/" then
			return find_venv(parent)
		end
		return nil
	end

	return find_venv(current_dir)
end

-- Use an on_attach function to only map the following keys
-- after the language server attaches to the current buffer
local on_attach = function(client, bufnr)
	local function buf_set_keymap(...)
		vim.api.nvim_buf_set_keymap(bufnr, ...)
	end
	local function buf_set_option(...)
		vim.api.nvim_buf_set_option(bufnr, ...)
	end

	--Enable completion triggered by <c-x><c-o>
	buf_set_option("omnifunc", "v:lua.vim.lsp.omnifunc")

	-- Mappings.
	local opts = { noremap = true, silent = true }

	-- See `:help vim.lsp.*` for documentation on any of the below functions
	buf_set_keymap("n", "gD", "<Cmd>lua vim.lsp.buf.declaration()<CR>", opts)
	buf_set_keymap("n", "gd", "<Cmd>lua vim.lsp.buf.definition()<CR>", opts)
	buf_set_keymap("n", "K", "<Cmd>lua vim.lsp.buf.hover()<CR>", opts)
	buf_set_keymap("n", "gi", "<cmd>lua vim.lsp.buf.implementation()<CR>", opts)
	buf_set_keymap("n", "<C-k>", "<cmd>lua vim.lsp.buf.signature_help()<CR>", opts)
	buf_set_keymap("n", "<space>wa", "<cmd>lua vim.lsp.buf.add_workspace_folder()<CR>", opts)
	buf_set_keymap("n", "<space>wr", "<cmd>lua vim.lsp.buf.remove_workspace_folder()<CR>", opts)
	buf_set_keymap("n", "<space>wl", "<cmd>lua print(vim.inspect(vim.lsp.buf.list_workspace_folders()))<CR>", opts)
	buf_set_keymap("n", "<space>D", "<cmd>lua vim.lsp.buf.type_definition()<CR>", opts)
	buf_set_keymap("n", "<space>rn", "<cmd>lua vim.lsp.buf.rename()<CR>", opts)
	buf_set_keymap("n", "<space>ca", "<cmd>lua vim.lsp.buf.code_action()<CR>", opts)
	buf_set_keymap("n", "gr", "<cmd>lua vim.lsp.buf.references()<CR>", opts)
	buf_set_keymap("n", "<space>e", "<cmd>lua vim.diagnostic.open_float()<CR>", opts)
	buf_set_keymap("n", "[d", "<cmd>lua vim.diagnostic.goto_prev()<CR>", opts)
	buf_set_keymap("n", "]d", "<cmd>lua vim.diagnostic.goto_next()<CR>", opts)
	buf_set_keymap("n", "<space>q", "<cmd>lua vim.diagnostic.setloclist()<CR>", opts)
	buf_set_keymap("n", "<space>f", "<cmd>lua vim.lsp.buf.format()<CR>", opts)
end

-- LSP server configurations
local servers = {
	rust_analyzer = {
		cmd = { "rust-analyzer" },
		filetypes = { "rust" },
		root_patterns = { "Cargo.toml", "rust-project.json" },
	},
	ts_ls = {
		cmd = { "typescript-language-server", "--stdio" },
		filetypes = { "javascript", "javascriptreact", "typescript", "typescriptreact" },
		root_patterns = { "package.json", "tsconfig.json", "jsconfig.json" },
	},
	ruff = {
		cmd = { "ruff", "server" },
		filetypes = { "python" },
		root_patterns = { "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile" },
	},
	pyright = {
		cmd = { "pyright-langserver", "--stdio" },
		filetypes = { "python" },
		root_patterns = {
			"pyproject.toml",
			"setup.py",
			"setup.cfg",
			"requirements.txt",
			"Pipfile",
			"pyrightconfig.json",
		},
		settings = function(root_dir, bufnr)
			local filepath = vim.api.nvim_buf_get_name(bufnr)

			-- For uv scripts, trigger async resolution if not cached
			if is_uv_script(bufnr) and not uv_python_cache[filepath] then
				resolve_uv_python_async(bufnr, filepath)
			end

			return {
				pyright = {
					disableOrganizeImports = true,
				},
				python = {
					pythonPath = get_python_path(bufnr),
					analysis = {
						ignore = { "*" },
						typeCheckingMode = "off",
					},
				},
			}
		end,
	},
}

-- Setup LSP servers using modern vim.lsp API
for server_name, config in pairs(servers) do
	vim.api.nvim_create_autocmd("FileType", {
		pattern = config.filetypes,
		callback = function(args)
			local root_dir = vim.fs.root(args.buf, config.root_patterns)
			local settings = config.settings
			if type(settings) == "function" then
				settings = settings(root_dir, args.buf)
			end

			local client_config = vim.tbl_deep_extend("force", config, {
				name = server_name,
				root_dir = root_dir,
				settings = settings,
				on_attach = function(client, bufnr)
					on_attach(client, bufnr)
				end,
			})
			-- Remove the function version of settings to avoid conflicts
			client_config.settings = settings

			vim.lsp.start(client_config)
		end,
	})
end
