return {
	{
		"nvim-treesitter/nvim-treesitter",
		lazy = false,
		build = function()
			require("nvim-treesitter").install({
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
			}):wait()
		end,
		config = function()
			vim.api.nvim_create_autocmd("FileType", {
				callback = function(args)
					if vim.bo[args.buf].filetype ~= "markdown" then
						pcall(vim.treesitter.start, args.buf)
					end
				end,
			})
		end,
	},
}
