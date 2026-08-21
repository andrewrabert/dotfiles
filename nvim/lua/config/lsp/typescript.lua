-- typescript-language-server, for JavaScript and TypeScript alike

vim.api.nvim_create_autocmd("FileType", {
	pattern = { "javascript", "javascriptreact", "typescript", "typescriptreact" },
	callback = function(args)
		vim.lsp.start({
			name = "ts_ls",
			cmd = { "typescript-language-server", "--stdio" },
			root_dir = vim.fs.root(args.buf, { "package.json", "tsconfig.json", "jsconfig.json" }),
		}, { bufnr = args.buf })
	end,
})
