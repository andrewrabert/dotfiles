-- rust-analyzer

vim.api.nvim_create_autocmd("FileType", {
	pattern = "rust",
	callback = function(args)
		vim.lsp.start({
			name = "rust_analyzer",
			cmd = { "rust-analyzer" },
			root_dir = vim.fs.root(args.buf, { "Cargo.toml", "rust-project.json" }),
		}, { bufnr = args.buf })
	end,
})
