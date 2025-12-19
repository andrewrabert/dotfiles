-- Modern LSP setup using vim.lsp.start instead of deprecated lspconfig

-- Cache for uv script venv roots (filepath -> venv_root)
local uv_venv_cache = {}

-- Check if a buffer is a uv inline script (has --script in shebang)
local function is_uv_script(bufnr)
	local first_line = vim.api.nvim_buf_get_lines(bufnr, 0, 1, false)[1] or ""
	return first_line:match("^#!.-uv.-run.-%-%-script") ~= nil
end

-- Blocking resolve uv script venv root
local function resolve_uv_venv_sync(filepath)
	if uv_venv_cache[filepath] then
		return uv_venv_cache[filepath]
	end

	-- Run uv sync --dry-run --offline to get env path without network/changes
	local cmd = { "uv", "sync", "--dry-run", "--offline", "--script", filepath }
	local result = vim.system(cmd, { text = true }):wait()
	local output = (result.stderr or "") .. (result.stdout or "")
	local env_path = output:match("Would %w+ script environment at: ([^\n]+)")
	if env_path then
		uv_venv_cache[filepath] = env_path
		return env_path
	end
	return nil
end

-- Find venv root by searching up from dir
local function find_venv_root(dir)
	local venv_names = { ".venv", "env" }
	for _, venv_name in ipairs(venv_names) do
		local venv_dir = dir .. "/" .. venv_name
		if vim.fn.filereadable(venv_dir .. "/bin/python") == 1 then
			return venv_dir
		end
	end
	local parent = vim.fn.fnamemodify(dir, ":h")
	if parent ~= dir and parent ~= "/" then
		return find_venv_root(parent)
	end
	return nil
end

-- Get venv root directory for a buffer
local function get_venv_root(bufnr)
	local filepath = vim.api.nvim_buf_get_name(bufnr)
	if is_uv_script(bufnr) then
		return resolve_uv_venv_sync(filepath)
	end
	local current_dir = vim.fn.expand("#" .. bufnr .. ":p:h")
	return find_venv_root(current_dir)
end

-- Get python path for a buffer
local function get_python_path(bufnr)
	local venv_root = get_venv_root(bufnr)
	if venv_root then
		return venv_root .. "/bin/python"
	end
	return nil
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
	-- ty = {
	-- 	cmd = { "ty", "server" },
	-- 	filetypes = { "python" },
	-- 	root_patterns = { "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile" },
	-- 	cmd_env = function(bufnr)
	-- 		local venv_root = get_venv_root(bufnr)
	-- 		if venv_root then
	-- 			return { VIRTUAL_ENV = venv_root }
	-- 		end
	-- 	end,
	-- },
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
			local cmd_env = config.cmd_env
			if type(cmd_env) == "function" then
				cmd_env = cmd_env(args.buf)
			end

			local client_config = vim.tbl_deep_extend("force", config, {
				name = server_name,
				root_dir = root_dir,
				settings = settings,
				cmd_env = cmd_env,
				on_attach = function(client, bufnr)
					on_attach(client, bufnr)
				end,
			})
			-- Remove function versions to avoid conflicts
			client_config.settings = settings
			client_config.cmd_env = cmd_env

			vim.lsp.start(client_config)
		end,
	})
end
