local M = {}

function M:peek(job)
	local file = job.file.url

	-- Run your preview command for audio files
	local cmd = Command("preview"):arg("--"):arg(tostring(file)):stdout(Command.PIPED):stderr(Command.PIPED)

	local child = cmd:spawn()
	if child then
		local output = child:wait_with_output()
		if output and output.status.success then
			ya.preview_widgets(job, {
				ui.Text
					.parse(output.stdout)
					:area(job.area)
					:wrap(rt.preview.wrap == "yes" and ui.Wrap.YES or ui.Wrap.NO),
			})
		else
			ya.preview_widgets(job, {
				ui.Text("Preview command failed")
					:area(job.area)
					:wrap(rt.preview.wrap == "yes" and ui.Wrap.YES or ui.Wrap.NO),
			})
		end
	else
		ya.preview_widgets(job, {
			ui.Text("Could not run preview command")
				:area(job.area)
				:wrap(rt.preview.wrap == "yes" and ui.Wrap.YES or ui.Wrap.NO),
		})
	end
end

return M
