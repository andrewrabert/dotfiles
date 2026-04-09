require("conform").setup({
	formatters_by_ft = {
		lua = { "stylua" },
		python = { "ruff_format", "ruff_fix" },
	},
	format_on_save = {
		timeout_ms = 500,
		lsp_fallback = false,
	},
	formatters = {
		ruff_format = {
			command = "ruff",
			args = { "format", "--stdin-filename", "$FILENAME", "-" },
		},
		ruff_fix = {
			command = "ruff",
			args = { "check", "--fix", "--exit-zero", "--stdin-filename", "$FILENAME", "-" },
		},
	},
})

vim.keymap.set("", "<leader>f", function()
	require("conform").format({ async = true, lsp_fallback = true })
end, { desc = "Format buffer" })
