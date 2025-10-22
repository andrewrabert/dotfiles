-- https://github.com/hrsh7th/nvim-cmp
local cmp = require("cmp")
local mapping = require("cmp.config.mapping")
local luasnip = require("luasnip")
local types = require("cmp.types")

require("luasnip.loaders.from_vscode").lazy_load()
vim.api.nvim_command("hi LuasnipChoiceNodePassive cterm=italic")

vim.opt.completeopt = "menu,menuone,noselect"

cmp.setup({
	snippet = {
		expand = function(args)
			require("luasnip").lsp_expand(args.body)
		end,
	},
	formatting = {
		format = function(entry, vim_item)
			local alias = {
				buffer = "buffer",
				path = "path",
				nvim_lsp = "LSP",
				luasnip = "LuaSnip",
				nvim_lua = "Lua",
			}

			if entry.source.name == "nvim_lsp" then
				vim_item.menu = entry.source.source.client.name
			else
				vim_item.menu = alias[entry.source.name] or entry.source.name
			end
			return vim_item
		end,
	},
	mapping = {
		["<C-b>"] = cmp.mapping(cmp.mapping.scroll_docs(-4), { "i", "c" }),
		["<C-f>"] = cmp.mapping(cmp.mapping.scroll_docs(4), { "i", "c" }),
		["<Tab>"] = cmp.mapping.confirm({ select = true }),
		["<C-n>"] = mapping({
			i = mapping.select_next_item({ behavior = types.cmp.SelectBehavior.Select }),
			c = function(fallback)
				local cmp = require("cmp")
				cmp.close()
				vim.schedule(cmp.suspend())
				fallback()
			end,
		}),
		["<C-p>"] = mapping({
			i = mapping.select_prev_item({ behavior = types.cmp.SelectBehavior.Select }),
			c = function(fallback)
				local cmp = require("cmp")
				cmp.close()
				vim.schedule(cmp.suspend())
				fallback()
			end,
		}),
	},
	sources = cmp.config.sources({
		{ name = "nvim_lsp", priority = 10 },
		{ name = "luasnip" },
	}, {
		{ name = "nvim_lua" },
	}, {
		{ name = "buffer" },
		{ name = "path" },
		{ name = "rg" },
	}),
})
