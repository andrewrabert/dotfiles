return {
	{
		"tinted-theming/tinted-vim",
		lazy = false,
		priority = 1000,
		config = function()
			local function is_tmux()
				return vim.env.TMUX ~= nil
			end
			local function is_ssh()
				return vim.env.SSH_CONNECTION ~= nil or vim.env.SSH_CLIENT ~= nil or vim.env.SSH_TTY ~= nil
			end

			local colorscheme = "base16-default-dark"

			vim.g.tinted_italic = 0
			vim.g.tinted_strikethrough = 0
			if vim.env.BASE16_THEME or is_tmux() or is_ssh() then
				vim.o.termguicolors = false
				vim.g.tinted_colorspace = 256
			else
				vim.o.termguicolors = true
			end

			local base16_path = vim.fs.normalize("~/.base16_theme")
			if vim.fn.filereadable(base16_path) then
				local base16_path_resolved = vim.fn.resolve(base16_path)
				if base16_path_resolved ~= "" and base16_path_resolved ~= base16_path then
					colorscheme = vim.fn.fnamemodify(base16_path_resolved, ":t:r")
				end
			end
			vim.cmd.colorscheme(colorscheme)

			vim.api.nvim_set_hl(0, "DiagnosticDeprecated", {
				ctermbg = 17,
			})
		end,
	},
}
