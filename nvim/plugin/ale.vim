" Disable ALE's LSP features to avoid conflicts with native LSP
let g:ale_disable_lsp = 1

" Only use ALE for linting, not LSP
let g:ale_linters = {
\   'python': [],
\}

" Disable ALE fixers for Python since you're using conform.nvim with ruff
let g:ale_fixers = {
\   'python': [],
\}

" Disable ALE completion since you're using nvim-cmp
let g:ale_completion_enabled = 0