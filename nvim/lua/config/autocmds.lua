local augroup = vim.api.nvim_create_augroup("Main", {})

vim.api.nvim_create_autocmd("StdinReadPre", {
	group = augroup,
	pattern = "*",
	callback = function()
		vim.g.std_in = 1
	end,
})

vim.api.nvim_create_autocmd("BufWritePost", {
	group = augroup,
	pattern = "*",
	callback = function()
		vim.uv.spawn("lmk", {})
	end,
})

vim.api.nvim_create_autocmd("VimResized", {
	group = augroup,
	pattern = "*",
	command = "wincmd =",
})

vim.api.nvim_create_autocmd("CursorHold", {
	group = augroup,
	callback = function()
		if _G.diagnostic_auto_popup_enabled() and vim.diagnostic.is_enabled() then
			vim.diagnostic.open_float(nil, { focus = false })
		end
	end,
})

vim.api.nvim_create_autocmd({ "BufRead", "BufNewFile" }, {
	group = vim.api.nvim_create_augroup("UvShebangDetection", {}),
	desc = "Set filetype to python for uv script files",
	callback = function()
		local line = vim.fn.getline(1)
		if line:match("^#!/usr/bin/env.*uv.*run") then
			vim.api.nvim_set_option_value("filetype", "python", { buf = 0 })
		end
	end,
})
