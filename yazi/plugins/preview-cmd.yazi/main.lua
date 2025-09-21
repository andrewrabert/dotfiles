local M = {}

function M:peek(job)
	local output, err = Command("preview"):arg({ tostring(job.file.url) }):stdout(Command.PIPED):output()

	local text
	if output then
		text = ui.Text(output.stdout)
	else
		text = ui.Text(string.format("Failed to start `preview`, error: %s", err))
	end

	ya.preview_widget(job, text:area(job.area):wrap(ui.Wrap.YES))
end

function M:seek() end

return M