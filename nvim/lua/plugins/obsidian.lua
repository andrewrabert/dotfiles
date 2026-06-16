require("obsidian").setup({
	legacy_commands = false,
	workspaces = {
		{
			name = "notes",
			path = "~/src/notes",
		},
	},
})

vim.keymap.set("n", "<leader>o", "<cmd>Obsidian<cr>", { desc = "Obsidian command palette" })
