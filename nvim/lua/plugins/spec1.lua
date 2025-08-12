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
  {"hrsh7th/cmp-buffer"},
  {"hrsh7th/cmp-cmdline"},
  {"hrsh7th/cmp-nvim-lsp"},
  {"hrsh7th/cmp-path"},
  {"hrsh7th/nvim-cmp"},
  {"neovim/nvim-lspconfig"},

  {"Vimjas/vim-python-pep8-indent"},

  {"godlygeek/tabular"},
  {"plasticboy/vim-markdown"},
  {"dhruvasagar/vim-table-mode"},

  {"junegunn/fzf"},
  {"junegunn/fzf.vim"},
  {"L3MON4D3/LuaSnip"},

  {"ledger/vim-ledger"},

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
                disable = { 
                    -- breaks gx on urls
                    "markdown",
                },
            },
        })
    end,
  },
  {"dense-analysis/ale"},
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
        show_help = '<f1>',
      },
    },
  },
}
