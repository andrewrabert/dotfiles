require("config.buffers")
require("config.lazy")
require("config.cmp")
require("config.lsp")

vim.o.ruler = true
vim.o.tabstop = 4
vim.o.shiftwidth = 4
vim.o.expandtab = true
vim.o.wrap = false
vim.o.cursorline = true
vim.o.hidden = true

vim.wo.foldmethod = 'expr'
vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()'

-- case insensitive search
vim.o.ignorecase = true

vim.g.tex_flavor = "latex"

-- line numbers
vim.o.number = true
vim.o.relativenumber = true

vim.o.mouse = "a"

do
    -- false so default uses base terminal colors.
    -- true breaks base16 themes
    local colorscheme = 'default'
    vim.o.termguicolors = false
    local base16_path = vim.fs.normalize('~/.base16_theme')
    if vim.fn.filereadable(base16_path) then
        local proc = vim.system({'readlink', base16_path}, { text = true }):wait()
        if proc.code == 0 then
            -- remove .sh suffix
            vim.g.tinted_colorspace = 256
            vim.g.tinted_italic = 0
            colorscheme = vim.fs.basename(string.sub(proc.stdout, 0, -5))
        end
    end
    vim.cmd.colorscheme(colorscheme)
end

vim.api.nvim_set_keymap("n", "<C-n>", ":set number!<CR>:set relativenumber!<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("n", "<C-c>", ":set cursorcolumn!<CR>", { noremap = true, silent = true })

vim.api.nvim_set_keymap("n", "<leader>z", ":Files<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("n", "<leader>x", ":Notes<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("n", "<leader>r", ":Rg<CR>", { noremap = true, silent = true })

vim.cmd([[

" relative percentage to screen
let g:lf_width = 1.0
let g:lf_height = 1.0

filetype plugin indent on

let $FZF_DEFAULT_COMMAND = "fd --type file --ignore-file ~/.config/nvim/fzf_fd_ignore"
let g:fzf_preview_window = ['right,50%,<70(hidden,right,50%)', 'ctrl-/']

autocmd StdinReadPre * let s:std_in=1

autocmd BufWritePost * call system("lmk")

let g:markdown_enable_spell_checking = 0

autocmd VimResized * wincmd =

" need to set both + and * else netrw barfs
let g:clipboard = {'copy': {'*': 'cbcopy', '+': 'cbcopy'}, 'paste': {'*': 'cbpaste', '+': 'cbpaste'}}
]])

vim.filetype.add({
  pattern = {
    ['.*/*.ASM'] = 'nasm',
    ['.*/*.MD'] = 'markdown',
  },
})

