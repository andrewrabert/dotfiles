-- Treesitter grammar install hook
vim.api.nvim_create_autocmd('PackChanged', {
	callback = function(ev)
		local name, kind = ev.data.spec.name, ev.data.kind
		if name == 'nvim-treesitter' and (kind == 'install' or kind == 'update') then
			if not ev.data.active then
				vim.cmd.packadd('nvim-treesitter')
			end
			require("nvim-treesitter").install({
				"bash", "c", "c_sharp", "cmake", "cpp", "css", "csv", "diff",
				"dockerfile", "html", "json", "lua", "markdown", "python", "rust", "yaml",
			}):wait()
		end
	end,
})

vim.pack.add({
	'https://github.com/tinted-theming/tinted-vim',
	'https://github.com/neovim/nvim-lspconfig',
	'https://github.com/ibhagwan/fzf-lua',
	'https://github.com/Vimjas/vim-python-pep8-indent',
	'https://github.com/godlygeek/tabular',
	'https://github.com/plasticboy/vim-markdown',
	'https://github.com/dhruvasagar/vim-table-mode',
	'https://github.com/stevearc/conform.nvim',
	'https://github.com/nvim-treesitter/nvim-treesitter',
	'https://github.com/hrsh7th/cmp-buffer',
	'https://github.com/hrsh7th/cmp-cmdline',
	'https://github.com/hrsh7th/cmp-nvim-lsp',
	'https://github.com/hrsh7th/cmp-path',
	'https://github.com/L3MON4D3/LuaSnip',
	'https://github.com/hrsh7th/nvim-cmp',
	'https://github.com/nvim-lua/plenary.nvim',
	'https://github.com/mikavilpas/yazi.nvim',
})

-- Plugin configurations
require("plugins.tinted")
require("plugins.fuzzy")
require("plugins.formatting")
require("plugins.treesitter")
require("plugins.completion")
require("plugins.yazi")
