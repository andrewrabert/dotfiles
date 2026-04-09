vim.pack.add({
	'https://github.com/tinted-theming/tinted-vim',
	'https://github.com/ibhagwan/fzf-lua',
	'https://github.com/Vimjas/vim-python-pep8-indent',
	'https://github.com/godlygeek/tabular',
	'https://github.com/plasticboy/vim-markdown',
	'https://github.com/dhruvasagar/vim-table-mode',
	'https://github.com/stevearc/conform.nvim',
	'https://github.com/nvim-lua/plenary.nvim',
	'https://github.com/mikavilpas/yazi.nvim',
})

-- Plugin configurations
require("plugins.tinted")
require("plugins.fuzzy")
require("plugins.formatting")
require("plugins.completion")
require("plugins.yazi")
