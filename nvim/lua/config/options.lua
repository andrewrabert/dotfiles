vim.o.ruler = true
vim.o.tabstop = 4
vim.o.shiftwidth = 4
vim.o.expandtab = true
vim.o.wrap = false
vim.o.cursorline = true
vim.o.hidden = true

vim.wo.foldmethod = "expr"
vim.wo.foldexpr = "v:lua.vim.treesitter.foldexpr()"
vim.wo.foldlevel = 99

-- case insensitive search
vim.o.ignorecase = true

-- line numbers
vim.o.number = true
vim.o.relativenumber = true

vim.o.mouse = "a"

-- terminal title
vim.opt.title = true
vim.opt.titlelen = 0
vim.opt.titlestring = 'nvim %{&buftype == "" ? expand("%:p") : expand("#:p")}'

-- show diagnostic popups faster (default 4000)
vim.o.updatetime = 500

vim.g.markdown_enable_spell_checking = 0

vim.g.clipboard = {
	copy = {
		["*"] = "cbcopy",
		["+"] = "cbcopy",
	},
	paste = {
		["*"] = "cbpaste",
		["+"] = "cbpaste",
	},
}

vim.filetype.add({
	pattern = {
		[".*/*.ASM"] = "nasm",
		[".*/*.MD"] = "markdown",
	},
})
