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
		-- not in formatters_by_ft; only run explicitly (e.g. :JSON)
		json_sort = {
			command = function()
				return vim.fn.executable("jaq") == 1 and "jaq" or "jq"
			end,
			args = function(_, ctx)
				return { "-S", "--indent", ctx.shiftwidth, "." }
			end,
		},
	},
})

vim.keymap.set("", "<leader>f", function()
	require("conform").format({ async = true, lsp_fallback = true })
end, { desc = "Format buffer" })
