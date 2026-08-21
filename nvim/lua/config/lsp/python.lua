-- Python language servers, and the uv environment ty needs to resolve imports
-- Every environment location comes from uv itself, never from inspecting the filesystem
-- Nothing here blocks: uv always runs as a background job, and ty starts from its callback

-- Resolve the environment uv governs a buffer with, and call back with it
-- A uv inline script gets `uv sync`, which builds the environment when it is
-- absent and confirms it in about 13 ms when it is not, so the same call both
-- reports the location and makes it real; uv ignores an ambient VIRTUAL_ENV for
-- scripts, so that branch is tested first
-- Any other buffer takes an ambient VIRTUAL_ENV, then asks uv what its directory
-- resolves to, as a dry run, because syncing someone's project on file open would
-- install into it uninvited; `Would use` means uv found one, `Would create` did not
---@param bufnr integer
---@param on_done fun(venv_root: string?)
local function resolve_env(bufnr, on_done)
	local filepath = vim.api.nvim_buf_get_name(bufnr)
	local first_line = vim.api.nvim_buf_get_lines(bufnr, 0, 1, false)[1] or ""

	if not first_line:match("^#!.-uv.-run.-%-%-script") then
		if vim.env.VIRTUAL_ENV then
			on_done(vim.env.VIRTUAL_ENV)
			return
		end
		local dir = vim.fs.dirname(filepath) or vim.fn.getcwd()
		vim.system({ "uv", "sync", "--dry-run", "--directory", dir }, { text = true }, function(result)
			vim.schedule(function()
				local output = (result.stdout or "") .. (result.stderr or "")
				on_done(output:match("Would use project environment at: ([^\n]+)"))
			end)
		end)
		return
	end

	local name = vim.fs.basename(filepath)
	vim.notify("uv: syncing script environment for " .. name, vim.log.levels.INFO)
	vim.system({ "uv", "sync", "--script", filepath }, { text = true }, function(result)
		vim.schedule(function()
			if result.code ~= 0 then
				local reason = vim.split(vim.trim(result.stderr or ""), "\n")[1]
				vim.notify("uv: script environment failed for " .. name .. ": " .. reason, vim.log.levels.ERROR)
				on_done(nil)
				return
			end
			vim.notify("uv: script environment synced for " .. name, vim.log.levels.INFO)
			local output = (result.stdout or "") .. (result.stderr or "")
			on_done(output:match("script environment at: ([^\n]+)"))
		end)
	end)
end

-- A loose script has no root_dir, so name and root_dir alone would make every
-- script share one client, and with it the first script's interpreter
---@param client vim.lsp.Client
---@param config vim.lsp.ClientConfig
---@return boolean
local function reuse_ty(client, config)
	if client.name ~= config.name or client:is_stopped() then
		return false
	end
	if client.config.root_dir ~= config.root_dir then
		return false
	end
	local client_env = client.config.cmd_env or {}
	local config_env = config.cmd_env or {}
	return client_env.VIRTUAL_ENV == config_env.VIRTUAL_ENV
end

local servers = {
	ruff = {
		cmd = { "ruff", "server" },
		root_patterns = { "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile" },
	},
	ty = {
		cmd = { "ty", "server" },
		root_patterns = { "pyproject.toml", "ty.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile" },
		reuse_client = reuse_ty,
	},
}

---@param server_name string
---@param bufnr integer
---@param venv_root string?
local function start_server(server_name, bufnr, venv_root)
	local config = servers[server_name]

	vim.lsp.start({
		name = server_name,
		cmd = config.cmd,
		root_dir = vim.fs.root(bufnr, config.root_patterns),
		cmd_env = venv_root and { VIRTUAL_ENV = venv_root } or nil,
	}, { bufnr = bufnr, reuse_client = config.reuse_client })
end

vim.api.nvim_create_autocmd("FileType", {
	pattern = "python",
	callback = function(args)
		start_server("ruff", args.buf)
		resolve_env(args.buf, function(venv_root)
			-- the buffer can be gone, or hold another file, by the time uv answers
			if vim.api.nvim_buf_is_valid(args.buf) then
				start_server("ty", args.buf, venv_root)
			end
		end)
	end,
})
