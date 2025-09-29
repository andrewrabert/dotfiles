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

  {"godlygeek/tabular"},
  {"plasticboy/vim-markdown"},
  {"dhruvasagar/vim-table-mode"},

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
      })
    end,
  },
  {"L3MON4D3/LuaSnip"},

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
                    "python"
                },
                disable = {
                    -- breaks gx on urls
                    "markdown",
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
        show_help = '<f1>',
      },
    },
  },
}
