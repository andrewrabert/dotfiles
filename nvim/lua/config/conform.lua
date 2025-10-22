require("conform").setup({
	formatters_by_ft = {
		python = { "ruff_format" },
		lua = { "stylua" },
	},
})
