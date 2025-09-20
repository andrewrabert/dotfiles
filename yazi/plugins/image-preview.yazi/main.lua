local M = {}

function M:peek(job)
	local start, url = os.clock(), ya.file_cache(job)
	if not url or not fs.cha(url) then
		url = job.file.url
	end

	ya.sleep(math.max(0, rt.preview.image_delay / 1000 + start - os.clock()))

	-- Calculate areas - reserve space for preview command output
	local text_lines = 5
	local image_area = ui.Rect {
		x = job.area.x,
		y = job.area.y,
		w = job.area.w,
		h = job.area.h - text_lines - 1
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
			for line in output.stdout:gmatch("[^\r\n]+") do
				table.insert(lines, line)
				if #lines >= text_lines - 1 then break end
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
			y = job.area.y + image_area.h + 1,
			w = job.area.w,
			h = text_lines
		}
		
		ya.preview_widgets(job, {
			ui.Text.parse(preview_text):area(text_area)
		})
	else
		ya.preview_widget(job, err)
	end
end

function M:seek() end

function M:preload(job)
	local cache = ya.file_cache(job)
	if not cache or fs.cha(cache) then
		return true
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
