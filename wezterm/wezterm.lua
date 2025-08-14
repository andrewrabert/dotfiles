local wezterm = require 'wezterm'

local config = {}

config.font = wezterm.font('Hack', { })
config.font_size = 14

config.enable_scroll_bar = false
config.enable_tab_bar = false
config.check_for_updates = false
config.window_close_confirmation = 'NeverPrompt'
config.force_reverse_video_cursor = true
config.native_macos_fullscreen_mode = true
config.window_padding = {
  left = 0,
  right = 0,
  top = 0,
  bottom = 0,
}

-- 120 fps is choppy at 120hz
config.max_fps = 255

return config
