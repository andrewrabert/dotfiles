if vim.fn.isdirectory(vim.fn.expand("~/src/notes/.obsidian")) == 0 then
	return
end

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
