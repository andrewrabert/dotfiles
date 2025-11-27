return {
	{
		"ibhagwan/fzf-lua",
		keys = {
			{ "<leader>z", "<cmd>FzfLua files<cr>", desc = "Find files" },
			{
				"<leader>Z",
				function()
					require("fzf-lua").files({ cwd = vim.fn.expand("%:p:h") })
				end,
				desc = "Find files in current dir",
			},
			{ "<leader>x", "<cmd>Notes<cr>", desc = "Notes" },
			{ "<leader>r", "<cmd>FzfLua live_grep<cr>", desc = "Live grep" },
			{
				"<leader>R",
				function()
					require("fzf-lua").live_grep({ search = vim.fn.expand("<cword>") })
				end,
				desc = "Grep word under cursor",
			},
		},
		config = function()
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
		end,
	},
}
