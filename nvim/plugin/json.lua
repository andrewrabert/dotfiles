vim.api.nvim_create_user_command("JSON", function()
	vim.bo.filetype = "json"
	require("conform").format({ formatters = { "json_sort" } })
end, {})
