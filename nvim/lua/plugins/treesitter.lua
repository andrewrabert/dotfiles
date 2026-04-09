vim.api.nvim_create_autocmd("FileType", {
	callback = function(args)
		if vim.bo[args.buf].filetype ~= "markdown" then
			pcall(vim.treesitter.start, args.buf)
		end
	end,
})
