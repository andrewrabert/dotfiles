return {
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
						"python",
					},
					disable = {
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
}
