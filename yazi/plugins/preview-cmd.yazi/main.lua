local M = {}

function M:peek(job)
	-- Check if we have cached preview content
	local cache_file = ya.file_cache(job)
	local cached_content = nil

	if cache_file and fs.cha(cache_file) then
		-- Read cached content
		local file = io.open(tostring(cache_file), "r")
		if file then
			cached_content = file:read("*all")
			file:close()
		end
	end

	local text
	if cached_content then
		text = ui.Text(cached_content)
	else
		-- Run preview command and cache result
        -- colors break wrapping
		local output, err = Command("preview"):arg({ "--no-color", "--", tostring(job.file.url) }):stdout(Command.PIPED):output()

		if output and output.stdout then
			text = ui.Text(output.stdout)

			-- Cache the output if we have a cache file path
			if cache_file then
				local file = io.open(tostring(cache_file), "w")
				if file then
					file:write(output.stdout)
					file:close()
				end
			end
		else
			text = ui.Text(string.format("Failed to start `preview`, error: %s", err))
		end
	end

	ya.preview_widget(job, text:area(job.area):wrap(rt.preview.wrap == "yes" and ui.Wrap.YES or ui.Wrap.NO))
end

function M:seek() end

function M:preload(job)
	local cache_file = ya.file_cache(job)
	if not cache_file or fs.cha(cache_file) then
		return true  -- Already cached or no cache path
	end

	-- Preload by running preview command and caching result
	local output, err = Command("preview"):arg({ "--", tostring(job.file.url) }):stdout(Command.PIPED):output()

	if output and output.stdout then
		local file = io.open(tostring(cache_file), "w")
		if file then
			file:write(output.stdout)
			file:close()
			return true
		end
	end

	return false
end

return M
