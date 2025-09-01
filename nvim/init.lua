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
vim.wo.foldlevel = 99

-- case insensitive search
vim.o.ignorecase = true

vim.g.tex_flavor = "latex"

-- line numbers
vim.o.number = true
vim.o.relativenumber = true

vim.o.mouse = "a"

-- terminal title
vim.opt.title = true
vim.opt.titlelen = 0
vim.opt.titlestring = 'nvim %{&buftype == "" ? expand("%:p") : expand("#:p")}'

do
    -- Function to check if running in TMUX
    local function is_tmux()
        return vim.env.TMUX ~= nil
    end

    -- Function to check if running over SSH
    local function is_ssh()
        return vim.env.SSH_CONNECTION ~= nil or vim.env.SSH_CLIENT ~= nil or vim.env.SSH_TTY ~= nil
    end


    -- false so default uses base terminal colors.
    -- true breaks base16 themes
    local colorscheme = 'base16-default-dark'

    vim.g.tinted_italic = 0
    if vim.env.BASE16_THEME or is_tmux() or is_ssh() then
        vim.o.termguicolors = false
        vim.g.tinted_colorspace = 256
    else
        -- eg. running nvim as the command to a gui terminal
        vim.o.termguicolors = true
    end

    local base16_path = vim.fs.normalize('~/.base16_theme')
    if vim.fn.filereadable(base16_path) then
        local base16_path_resolved = vim.fn.resolve(base16_path)
        if base16_path_resolved ~= "" and base16_path_resolved ~= base16_path then
            colorscheme = vim.fn.fnamemodify(base16_path_resolved, ":t:r")
        end
    end
    vim.cmd.colorscheme(colorscheme)
end

vim.api.nvim_set_keymap("n", "<C-n>", ":set number!<CR>:set relativenumber!<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("n", "<C-c>", ":set cursorcolumn!<CR>", { noremap = true, silent = true })

vim.api.nvim_set_keymap("n", "<leader>z", ":lua require('fzf-lua').files()<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("n", "<leader>x", ":Notes<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("n", "<leader>r", ":lua require('fzf-lua').live_grep()<CR>", { noremap = true, silent = true })
vim.keymap.set("n", "<leader>R", function()
    local word = vim.fn.expand("<cword>")
    require('fzf-lua').live_grep({ search = word })
end, { noremap = true, silent = true })

vim.keymap.set("n", "<leader>dt", function()
    vim.diagnostic.enable(not vim.diagnostic.is_enabled())
end)


vim.api.nvim_create_autocmd("StdinReadPre", {
  group = augroup,
  pattern = "*",
  callback = function()
    vim.g.std_in = 1
  end,
})

vim.api.nvim_create_autocmd("BufWritePost", {
  group = augroup,
  pattern = "*",
  callback = function()
    vim.fn.system("lmk")
  end,
})

vim.g.markdown_enable_spell_checking = 0

vim.api.nvim_create_autocmd("VimResized", {
  group = augroup,
  pattern = "*",
  command = "wincmd =",
})

vim.g.clipboard = {
  copy = {
    ['*'] = 'cbcopy',
    ['+'] = 'cbcopy'
  },
  paste = {
    ['*'] = 'cbpaste',
    ['+'] = 'cbpaste'
  }
}

vim.filetype.add({
  pattern = {
    ['.*/*.ASM'] = 'nasm',
    ['.*/*.MD'] = 'markdown',
  },
})

vim.keymap.set('n', '<leader>td', function()
  vim.diagnostic.enable(not vim.diagnostic.is_enabled())
end, { desc = 'Toggle diagnostics' })
