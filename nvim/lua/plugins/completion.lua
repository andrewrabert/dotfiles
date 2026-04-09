vim.opt.completeopt = "menu,menuone,noselect,popup"

vim.api.nvim_create_autocmd("LspAttach", {
	callback = function(ev)
		vim.lsp.completion.enable(true, ev.data.client_id, ev.buf, { autotrigger = true })
	end,
})
