local loop_a
local loop_b
local tmp_a

local function bouncing_loop(_, time_pos)
	if time_pos then
		local dir = mp.get_property("play-direction")
		if dir == "forward" and (time_pos >= loop_b) then
			mp.commandv("cycle", "play-direction")
		elseif dir == "backward" and (time_pos <= loop_a) then
			mp.commandv("cycle", "play-direction")
		end
	end
end

mp.add_key_binding(";", "bouncing-loop", function()
	if loop_a == nil then
		loop_a = mp.get_property_native("time-pos")
		mp.osd_message("A-B bounce-loop start " .. loop_a)
	elseif loop_b == nil then
		loop_b = mp.get_property_native("time-pos")
		if loop_a > loop_b then
			tmp_a = loop_a
			loop_a = loop_b
			loop_b = tmp_a
		elseif loop_a == loop_b then
			mp.osd_message("A and B cannot be the same, ignoring")
			loop_b = nil
			return
		end
		mp.observe_property("time-pos", "native", bouncing_loop)
		local path = mp.get_property("path")
		mp.msg.info(string.format("BOUNCE %s %s %s", loop_a, loop_b, path))
		print(string.format("BOUNCE %s %s %s", loop_a, loop_b, path))
		mp.osd_message("A-B bounce-loop " .. loop_a .. " - " .. loop_b)
	else
		mp.unobserve_property(bouncing_loop)
		mp.osd_message("Clear A-B bounce loop")
		mp.set_property("play-direction", "forward")
		loop_a = nil
		loop_b = nil
	end
end)
