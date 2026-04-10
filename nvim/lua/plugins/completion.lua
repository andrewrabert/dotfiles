require("blink.cmp").setup({
	keymap = {
		preset = "default",
		["<Tab>"] = { "accept", "fallback" },
	},
	completion = {
		list = {
			selection = { preselect = true, auto_insert = true },
		},
		documentation = {
			auto_show = true,
		},
		accept = {
			auto_brackets = { enabled = false },
		},
	},
	sources = {
		default = { "lsp", "path", "buffer" },
	},
})
