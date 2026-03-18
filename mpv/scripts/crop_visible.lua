-- Prints the ffmpeg crop filter for the currently visible region
-- when zoomed/panned in mpv. Bound to Alt+c.

function get_crop_params()
    local source_w = mp.get_property_number("video-params/w")
    local source_h = mp.get_property_number("video-params/h")
    local dw = mp.get_property_number("video-out-params/dw")
    local dh = mp.get_property_number("video-out-params/dh")
    local osd_w = mp.get_property_number("osd-width")
    local osd_h = mp.get_property_number("osd-height")
    local zoom = mp.get_property_number("video-zoom")
    local pan_x = mp.get_property_number("video-pan-x")
    local pan_y = mp.get_property_number("video-pan-y")

    if not source_w or not source_h then
        mp.osd_message("No video loaded")
        return
    end

    local scale = 2 ^ zoom
    local display_aspect = dw / dh
    local window_aspect = osd_w / osd_h

    -- base display size (zoom=0, fitted to window)
    local base_w, base_h
    if display_aspect > window_aspect then
        base_w = osd_w
        base_h = osd_w / display_aspect
    else
        base_h = osd_h
        base_w = osd_h * display_aspect
    end

    -- visible fraction of source video
    local frac_w = math.min(1, osd_w / (base_w * scale))
    local frac_h = math.min(1, osd_h / (base_h * scale))

    local crop_w = math.floor(source_w * frac_w)
    local crop_h = math.floor(source_h * frac_h)

    -- make even for ffmpeg
    crop_w = crop_w - (crop_w % 2)
    crop_h = crop_h - (crop_h % 2)

    -- visible center in source coordinates
    local cx = source_w * (0.5 - pan_x)
    local cy = source_h * (0.5 - pan_y)

    local crop_x = math.floor(cx - crop_w / 2)
    local crop_y = math.floor(cy - crop_h / 2)

    -- clamp
    crop_x = math.max(0, math.min(crop_x, source_w - crop_w))
    crop_y = math.max(0, math.min(crop_y, source_h - crop_h))

    return crop_w, crop_h, crop_x, crop_y
end

function show_crop()
    local w, h, x, y = get_crop_params()
    if not w then return end

    local zoom = mp.get_property_number("video-zoom")
    local pan_x = mp.get_property_number("video-pan-x")
    local pan_y = mp.get_property_number("video-pan-y")
    mp.msg.info(string.format("zoom=%.3f pan_x=%.4f pan_y=%.4f", zoom, pan_x, pan_y))
    mp.msg.info(string.format("crop=%d:%d:%d:%d", w, h, x, y))

    local input_path = mp.get_property("path")
    -- resolve relative paths against working-directory
    if input_path and not input_path:match("^/") then
        local wd = mp.get_property("working-directory")
        if wd then
            input_path = wd .. "/" .. input_path
        end
    end

    local base = input_path and input_path:match("([^/]+)%.[^.]+$") or "output"
    local timestamp = os.date("%Y%m%d%H%M%S")
    local output_path = string.format("%s_%s.mkv", base, timestamp)

    local ss = ""
    local to = ""
    local ab_a = mp.get_property_native("ab-loop-a")
    local ab_b = mp.get_property_native("ab-loop-b")
    if type(ab_a) == "number" then
        ss = string.format(" -ss %.3f", ab_a)
    end
    if type(ab_b) == "number" then
        to = string.format(" -to %.3f", ab_b)
    end

    local cmd = string.format(
        "ffmpeg%s%s -i '%s' -vf crop=%d:%d:%d:%d -c:v ffv1 -c:a copy '%s'",
        ss, to, input_path, w, h, x, y, output_path
    )

    mp.osd_message(cmd, 5)
    mp.command_native_async({
        name = "subprocess",
        args = {"wl-copy", cmd},
        playback_only = false,
        capture_stdout = false,
        capture_stderr = false,
    }, function() end)
    print(cmd)
end

mp.add_key_binding("Alt+c", "crop_visible", show_crop)
