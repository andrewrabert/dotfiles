require("blink.cmp").setup({
	keymap = {
		preset = "default",
		["<Tab>"] = { "accept", "fallback" },
	},
	completion = {
		list = {
			selection = { preselect = false, auto_insert = true },
		},
		documentation = {
			auto_show = true,
		},
	},
	sources = {
		default = { "lsp", "path", "buffer" },
	},
})
