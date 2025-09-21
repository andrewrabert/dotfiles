local M = {}

function M:peek(job)
	local start, url = os.clock(), ya.file_cache(job)
	if not url or not fs.cha(url) then
		url = job.file.url
	end

	-- Convert HEIF/HEIC/TIFF files to JPEG using vips
	local temp_file_to_cleanup = nil
	local file_ext = tostring(job.file.url):match("%.([^%.]+)$")
	if file_ext and (file_ext:lower() == "heic" or file_ext:lower() == "heif" or file_ext:lower() == "tiff" or file_ext:lower() == "tif") then
		local temp_file = "/tmp/yazi-convert-" .. ya.hash(tostring(job.file.url)) .. ".jpg"

		-- Convert to JPEG using vips
		local convert_cmd = Command("vips")
			:arg("jpegsave")
			:arg(tostring(job.file.url))
			:arg(temp_file)
			:stderr(Command.PIPED)

		local convert_result = convert_cmd:spawn()
		if convert_result and convert_result:wait().success then
			url = Url(temp_file)
			temp_file_to_cleanup = temp_file
		end
	end

	ya.sleep(math.max(0, rt.preview.image_delay / 1000 + start - os.clock()))

	-- Calculate areas - split 50%/50% between image and preview text
	local half_height = math.floor(job.area.h / 2)
	local image_area = ui.Rect {
		x = job.area.x,
		y = job.area.y,
		w = job.area.w,
		h = half_height
	}

	-- Show the image in the reduced area
	local _, err = ya.image_show(url, image_area)
	
	-- Get preview command output
	local cmd = Command("preview")
		:arg(tostring(job.file.url))
		:stdout(Command.PIPED)
		:stderr(Command.PIPED)
	
	local preview_text = ""
	local child = cmd:spawn()
	if child then
		local output = child:wait_with_output()
		if output and output.status.success and output.stdout and output.stdout ~= "" then
			local lines = {}
			local max_lines = job.area.h - half_height - 2  -- Use remaining space minus separator
			for line in output.stdout:gmatch("[^\r\n]+") do
				table.insert(lines, line)
				if #lines >= max_lines then break end
			end
			
			if #lines > 0 then
				local separator = string.rep("─", math.min(job.area.w, 60))
				preview_text = separator .. "\n" .. table.concat(lines, "\n")
			end
		end
	end
	
	-- Show preview text at bottom if we have any
	if preview_text ~= "" then
		local text_area = ui.Rect {
			x = job.area.x,
			y = job.area.y + half_height,
			w = job.area.w,
			h = job.area.h - half_height
		}
		
		ya.preview_widgets(job, {
			ui.Text.parse(preview_text):area(text_area):wrap(rt.preview.wrap == "yes" and ui.Wrap.YES or ui.Wrap.NO)
		})
	else
		ya.preview_widget(job, err)
	end

	-- Clean up temp file if created
	if temp_file_to_cleanup then
		Command("rm"):arg(temp_file_to_cleanup):spawn()
	end
end

function M:seek() end

function M:preload(job)
	local cache = ya.file_cache(job)
	if not cache or fs.cha(cache) then
		return true
	end

	-- Convert HEIF/HEIC/TIFF files to JPEG for preloading
	local file_ext = tostring(job.file.url):match("%.([^%.]+)$")
	if file_ext and (file_ext:lower() == "heic" or file_ext:lower() == "heif" or file_ext:lower() == "tiff" or file_ext:lower() == "tif") then
		local temp_file = "/tmp/yazi-convert-" .. ya.hash(tostring(job.file.url)) .. ".jpg"

		-- Convert to JPEG using vips
		local convert_cmd = Command("vips")
			:arg("jpegsave")
			:arg(tostring(job.file.url))
			:arg(temp_file)
			:stderr(Command.PIPED)

		local convert_result = convert_cmd:spawn()
		if convert_result and convert_result:wait().success then
			local result = ya.image_precache(Url(temp_file), cache)
			-- Clean up temp file after caching
			Command("rm"):arg(temp_file):spawn()
			return result
		end
	end

	return ya.image_precache(job.file.url, cache)
end

function M:spot(job)
	local rows = self:spot_base(job)
	rows[#rows + 1] = ui.Row {}

	ya.spot_table(
		job,
		ui.Table(ya.list_merge(rows, require("file"):spot_base(job)))
			:area(ui.Pos { "center", w = 60, h = 20 })
			:row(job.skip)
			:row(1)
			:col(1)
			:col_style(th.spot.tbl_col)
			:cell_style(th.spot.tbl_cell)
			:widths { ui.Constraint.Length(14), ui.Constraint.Fill(1) }
	)
end

function M:spot_base(job)
	local info = ya.image_info(job.file.url)
	if not info then
		return {}
	end

	return {
		ui.Row({ "Image" }):style(ui.Style():fg("green")),
		ui.Row { "  Format:", tostring(info.format) },
		ui.Row { "  Size:", string.format("%dx%d", info.w, info.h) },
		ui.Row { "  Color:", tostring(info.color) },
	}
end

return M
