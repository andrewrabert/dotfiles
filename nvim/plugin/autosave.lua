vim.g.autosave_enabled = false

vim.api.nvim_create_autocmd({ "InsertLeave", "TextChanged" }, {
	group = vim.api.nvim_create_augroup("AutoSave", {}),
	nested = true,
	callback = function()
		if vim.g.autosave_enabled then
			vim.cmd.update()
		end
	end,
})

vim.api.nvim_create_user_command("EnableAutoSave", function()
	vim.g.autosave_enabled = true
end, {})

vim.api.nvim_create_user_command("DisableAutoSave", function()
	vim.g.autosave_enabled = false
end, {})
