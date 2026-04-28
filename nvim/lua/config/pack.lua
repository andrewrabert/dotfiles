-- Delete plugins on disk but no longer in add() calls
local function pack_cleanup()
	local stale = vim.iter(vim.pack.get())
		:filter(function(x) return not x.active end)
		:map(function(x) return x.spec.name end)
		:totable()
	if #stale > 0 then
		vim.pack.del(stale, { force = true })
	end
end

vim.api.nvim_create_user_command("PackCleanup", pack_cleanup, {})
vim.api.nvim_create_user_command("PackSync", function()
	pack_cleanup()
	vim.pack.update(nil, { force = true })
	if not require('blink.cmp').library_available() then
		print('Building blink.cmp native library...')
		require('blink.cmp').build():wait(math.huge)
	end
end, {})

vim.pack.add({
	'https://github.com/tinted-theming/tinted-vim',
	'https://github.com/ibhagwan/fzf-lua',
	'https://github.com/Vimjas/vim-python-pep8-indent',
	'https://github.com/dhruvasagar/vim-table-mode',
	'https://github.com/stevearc/conform.nvim',
	'https://github.com/Saghen/blink.lib',
	'https://github.com/Saghen/blink.cmp',
	'https://github.com/nvim-lua/plenary.nvim',
	'https://github.com/mikavilpas/yazi.nvim',
})

-- Plugin configurations
require("plugins.tinted")
require("plugins.fuzzy")
require("plugins.formatting")
require("plugins.completion")
require("plugins.yazi")
