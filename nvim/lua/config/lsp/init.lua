-- Modern LSP setup using vim.lsp.start instead of deprecated lspconfig
-- One module per language, each starting the servers it owns

-- Extra keymaps not covered by Neovim LSP defaults (gra, grn, grr, gri, grt, K, etc.)
vim.api.nvim_create_autocmd("LspAttach", {
	callback = function(args)
		local opts = { buffer = args.buf, silent = true }
		vim.keymap.set("n", "gD", vim.lsp.buf.declaration, opts)
		vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
	end,
})

require("config.lsp.rust")
require("config.lsp.typescript")
require("config.lsp.python")
