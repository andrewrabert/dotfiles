-- buffer navigation
vim.keymap.set("n", "<leader>n", ":bn!<CR>")
vim.keymap.set("n", "<leader>p", ":bp!<CR>")
vim.keymap.set("n", "<leader>bd", ":bd<CR>")
vim.keymap.set("n", "<leader>3", ":b#<CR>")
vim.keymap.set("n", "<leader>l", ":buffers<CR>:buffer<Space>")
for i = 1, 9 do
	vim.keymap.set("n", "<leader>b" .. i, ":" .. i .. "b<CR>")
end

-- toggles
local silent = { silent = true }
vim.keymap.set("n", "<C-n>", function()
	vim.o.number = not vim.o.number
	vim.o.relativenumber = not vim.o.relativenumber
end, silent)
vim.keymap.set("n", "<C-c>", ":set cursorcolumn!<CR>", silent)
vim.keymap.set("n", "<leader>w", ":set wrap!<CR>", silent)

-- diagnostics
local diagnostic_auto_popup = true

vim.keymap.set("n", "<leader>D", function()
	vim.diagnostic.enable(not vim.diagnostic.is_enabled())
	diagnostic_auto_popup = false
end, { desc = "Toggle diagnostics (disable auto-popup)" })

vim.keymap.set("n", "<leader>d", function()
	diagnostic_auto_popup = not diagnostic_auto_popup
	if diagnostic_auto_popup and not vim.diagnostic.is_enabled() then
		vim.diagnostic.enable(true)
	end
	print("Diagnostic auto-popup: " .. (diagnostic_auto_popup and "enabled" or "disabled"))
end, { desc = "Toggle diagnostic auto-popup" })

-- expose for autocmds
_G.diagnostic_auto_popup_enabled = function()
	return diagnostic_auto_popup
end
