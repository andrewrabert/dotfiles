return {
	{
		"tinted-theming/tinted-vim",
		lazy = false,
		priority = 1000,
		config = function()
			-- load the colorscheme here
			vim.cmd([[colorscheme base16-default-dark]])
		end,
	},
	{ "hrsh7th/cmp-buffer" },
	{ "hrsh7th/cmp-cmdline" },
	{ "hrsh7th/cmp-nvim-lsp" },
	{ "hrsh7th/cmp-path" },
	{ "hrsh7th/nvim-cmp" },
	{ "neovim/nvim-lspconfig" },

	{ "Vimjas/vim-python-pep8-indent" },

	{ "godlygeek/tabular" },
	{ "plasticboy/vim-markdown" },
	{ "dhruvasagar/vim-table-mode" },

	{
		"ibhagwan/fzf-lua",
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
	{ "L3MON4D3/LuaSnip" },

	{
		"nvim-treesitter/nvim-treesitter",
		config = function()
			require("nvim-treesitter.configs").setup({
				ensure_installed = {
					"bash",
					"c",
					"c_sharp",
					"cmake",
					"cpp",
					"css",
					"csv",
					"diff",
					"dockerfile",
					"html",
					"json",
					"latex",
					"lua",
					"lua",
					"markdown",
					"python",
					"rust",
					"yaml",
				},
				sync_install = #vim.api.nvim_list_uis() == 0,
				highlight = {
					enable = true,
					additional_vim_regex_highlighting = {
						-- fixes indent when string contains [
						-- https://github.com/nvim-treesitter/nvim-treesitter/issues/1573
						"python",
					},
					disable = {
						-- breaks gx on urls
						"markdown",
					},
				},
				incremental_selection = {
					enable = true,
					keymaps = {
						init_selection = "gnn",
						node_incremental = "grn",
						scope_incremental = "grc",
						node_decremental = "grm",
					},
				},
			})
		end,
	},
	{
		"stevearc/conform.nvim",
		event = { "BufWritePre" },
		cmd = { "ConformInfo" },
		keys = {
			{
				"<leader>f",
				function()
					require("conform").format({ async = true, lsp_fallback = true })
				end,
				mode = "",
				desc = "Format buffer",
			},
		},
		opts = {
			formatters_by_ft = {
				lua = { "stylua" },
				python = { "ruff_format", "ruff_fix" },
			},
			format_on_save = {
				timeout_ms = 500,
				lsp_fallback = true,
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
		},
	},
	{
		"mikavilpas/yazi.nvim",
		event = "VeryLazy",
		keys = {
			{
				"<leader>-",
				"<cmd>Yazi<cr>",
				desc = "Open yazi at the current file",
			},
			{
				"<leader>cw",
				"<cmd>Yazi cwd<cr>",
				desc = "Open the file manager in nvim's working directory",
			},
		},
		opts = {
			open_for_directories = false,
			keymaps = {
				show_help = "<f1>",
			},
		},
	},
	{
		"coder/claudecode.nvim",
		dependencies = { "folke/snacks.nvim" },
		config = true,
		opts = {
			terminal = {
				snacks_win_opts = {
					wo = {
						winblend = 100,
						winhighlight = "NormalFloat:MyTransparentGroup",
					},
				},
			},
		},
		keys = {
			{ "<leader>a", nil, desc = "AI/Claude Code" },
			{ "<leader>ac", "<cmd>ClaudeCode<cr>", desc = "Toggle Claude" },
			{ "<leader>af", "<cmd>ClaudeCodeFocus<cr>", desc = "Focus Claude" },
			{ "<leader>ar", "<cmd>ClaudeCode --resume<cr>", desc = "Resume Claude" },
			{ "<leader>aC", "<cmd>ClaudeCode --continue<cr>", desc = "Continue Claude" },
			{ "<leader>am", "<cmd>ClaudeCodeSelectModel<cr>", desc = "Select Claude model" },
			{ "<leader>ab", "<cmd>ClaudeCodeAdd %<cr>", desc = "Add current buffer" },
			{ "<leader>as", "<cmd>ClaudeCodeSend<cr>", mode = "v", desc = "Send to Claude" },
			{
				"<leader>as",
				"<cmd>ClaudeCodeTreeAdd<cr>",
				desc = "Add file",
				ft = { "NvimTree", "neo-tree", "oil", "minifiles", "netrw" },
			},
			-- Diff management
			{ "<leader>aa", "<cmd>ClaudeCodeDiffAccept<cr>", desc = "Accept diff" },
			{ "<leader>ad", "<cmd>ClaudeCodeDiffDeny<cr>", desc = "Deny diff" },
		},
	},
}
