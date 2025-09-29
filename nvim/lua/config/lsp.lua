-- Modern LSP setup using vim.lsp.start instead of deprecated lspconfig

-- Use an on_attach function to only map the following keys
-- after the language server attaches to the current buffer
local on_attach = function(client, bufnr)
    local function buf_set_keymap(...)
        vim.api.nvim_buf_set_keymap(bufnr, ...)
    end
    local function buf_set_option(...)
        vim.api.nvim_buf_set_option(bufnr, ...)
    end

    --Enable completion triggered by <c-x><c-o>
    buf_set_option("omnifunc", "v:lua.vim.lsp.omnifunc")

    -- Mappings.
    local opts = { noremap = true, silent = true }

    -- See `:help vim.lsp.*` for documentation on any of the below functions
    buf_set_keymap("n", "gD", "<Cmd>lua vim.lsp.buf.declaration()<CR>", opts)
    buf_set_keymap("n", "gd", "<Cmd>lua vim.lsp.buf.definition()<CR>", opts)
    buf_set_keymap("n", "K", "<Cmd>lua vim.lsp.buf.hover()<CR>", opts)
    buf_set_keymap("n", "gi", "<cmd>lua vim.lsp.buf.implementation()<CR>", opts)
    buf_set_keymap("n", "<C-k>", "<cmd>lua vim.lsp.buf.signature_help()<CR>", opts)
    buf_set_keymap("n", "<space>wa", "<cmd>lua vim.lsp.buf.add_workspace_folder()<CR>", opts)
    buf_set_keymap("n", "<space>wr", "<cmd>lua vim.lsp.buf.remove_workspace_folder()<CR>", opts)
    buf_set_keymap("n", "<space>wl", "<cmd>lua print(vim.inspect(vim.lsp.buf.list_workspace_folders()))<CR>", opts)
    buf_set_keymap("n", "<space>D", "<cmd>lua vim.lsp.buf.type_definition()<CR>", opts)
    buf_set_keymap("n", "<space>rn", "<cmd>lua vim.lsp.buf.rename()<CR>", opts)
    buf_set_keymap("n", "<space>ca", "<cmd>lua vim.lsp.buf.code_action()<CR>", opts)
    buf_set_keymap("n", "gr", "<cmd>lua vim.lsp.buf.references()<CR>", opts)
    buf_set_keymap("n", "<space>e", "<cmd>lua vim.diagnostic.open_float()<CR>", opts)
    buf_set_keymap("n", "[d", "<cmd>lua vim.diagnostic.goto_prev()<CR>", opts)
    buf_set_keymap("n", "]d", "<cmd>lua vim.diagnostic.goto_next()<CR>", opts)
    buf_set_keymap("n", "<space>q", "<cmd>lua vim.diagnostic.setloclist()<CR>", opts)
    buf_set_keymap("n", "<space>f", "<cmd>lua vim.lsp.buf.format()<CR>", opts)
end

-- LSP server configurations
local servers = {
  rust_analyzer = {
    cmd = { 'rust-analyzer' },
    filetypes = { 'rust' },
    root_patterns = { 'Cargo.toml', 'rust-project.json' }
  },
  ts_ls = {
    cmd = { 'typescript-language-server', '--stdio' },
    filetypes = { 'javascript', 'javascriptreact', 'typescript', 'typescriptreact' },
    root_patterns = { 'package.json', 'tsconfig.json', 'jsconfig.json' }
  },
  ruff = {
    cmd = { 'ruff', 'server' },
    filetypes = { 'python' },
    root_patterns = { 'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt', 'Pipfile' }
  },
  pyright = {
    cmd = { 'basedpyright-langserver', '--stdio' },
    filetypes = { 'python' },
    root_patterns = { 'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt', 'Pipfile', 'pyrightconfig.json' },
    settings = function(root_dir, bufnr)
      local python_path = nil
      -- Start from the current file's directory and search up
      local current_dir = vim.fn.expand('#' .. bufnr .. ':p:h')
      local venv_names = { '.venv', 'env' }

      local function find_venv(dir)
        for _, venv_name in ipairs(venv_names) do
          local venv_python = dir .. '/' .. venv_name .. '/bin/python'
          if vim.fn.filereadable(venv_python) == 1 then
            return venv_python
          end
        end
        -- Check parent directory
        local parent = vim.fn.fnamemodify(dir, ':h')
        if parent ~= dir and parent ~= '/' then
          return find_venv(parent)
        end
        return nil
      end

      python_path = find_venv(current_dir)

      return {
        pyright = {
          disableOrganizeImports = true,
        },
        python = {
          pythonPath = python_path,
          analysis = {
            ignore = { '*' },
            typeCheckingMode = "off"
          }
        }
      }
    end
  }
}

-- Setup LSP servers using modern vim.lsp API
for server_name, config in pairs(servers) do
  vim.api.nvim_create_autocmd('FileType', {
    pattern = config.filetypes,
    callback = function(args)
      local root_dir = vim.fs.root(args.buf, config.root_patterns)
      local settings = config.settings
      if type(settings) == 'function' then
        settings = settings(root_dir, args.buf)
      end

      local client_config = vim.tbl_deep_extend('force', config, {
        name = server_name,
        root_dir = root_dir,
        settings = settings,
        on_attach = function(client, bufnr)
          on_attach(client, bufnr)
        end,
      })
      -- Remove the function version of settings to avoid conflicts
      client_config.settings = settings

      vim.lsp.start(client_config)
    end,
  })
end
