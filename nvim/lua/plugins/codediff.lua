require("codediff").setup()

vim.keymap.set("n", "<leader>gd", "<cmd>CodeDiff<cr>", { desc = "Diff working tree (explorer)" })
vim.keymap.set("n", "<leader>gD", "<cmd>CodeDiff HEAD<cr>", { desc = "Diff against HEAD" })
vim.keymap.set("n", "<leader>gh", "<cmd>CodeDiff history<cr>", { desc = "Commit history diffs" })
