local M = {}

function M:fetch(job)
	local urls = {}
	local updates = {}
	local state = {}

	for i, file in ipairs(job.files) do
		local url = tostring(file.url)
		urls[i] = url
		updates[url] = "image/jpeg"  -- Return empty string for all files
		state[i] = true
	end

	-- Emit the updates with empty MIME types
	if next(updates) then
		ya.emit("update_mimes", { updates = updates })
	end

	return state
end

return M
