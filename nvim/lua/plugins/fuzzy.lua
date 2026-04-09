require("fzf-lua").setup({
	winopts = {
		height = 0.85,
		width = 0.80,
		preview = {
			default = "bat",
			layout = "horizontal",
			horizontal = "right:50%",
		},
	},
	fzf_opts = {
		["--layout"] = "reverse-list",
	},
	files = {
		fd_opts = "--type f --hidden --follow --exclude .git --ignore-file "
			.. vim.fn.stdpath("config")
			.. "/fzf_fd_ignore",
	},
})

vim.keymap.set("n", "<leader>z", "<cmd>FzfLua files<cr>", { desc = "Find files" })
vim.keymap.set("n", "<leader>Z", function()
	require("fzf-lua").files({ cwd = vim.fn.expand("%:p:h") })
end, { desc = "Find files in current dir" })
vim.keymap.set("n", "<leader>x", "<cmd>Notes<cr>", { desc = "Notes" })
vim.keymap.set("n", "<leader>r", "<cmd>FzfLua live_grep<cr>", { desc = "Live grep" })
vim.keymap.set("n", "<leader>R", function()
	require("fzf-lua").live_grep({ search = vim.fn.expand("<cword>") })
end, { desc = "Grep word under cursor" })
