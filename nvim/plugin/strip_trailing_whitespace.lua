local function strip_trailing_whitespace()
	if vim.bo.binary or vim.bo.filetype == "diff" then
		return
	end
	local view = vim.fn.winsaveview()
	vim.cmd([[keeppatterns %s/\s\+$//e]])
	vim.fn.winrestview(view)
end

vim.api.nvim_create_user_command("FixEmpty", function()
	vim.bo.expandtab = true
	vim.cmd.retab()
	strip_trailing_whitespace()
	vim.cmd([[keeppatterns %s/\r//ge]])
end, {})
