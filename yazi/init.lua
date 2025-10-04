require("session"):setup {
    sync_yanked = true,
}

local old_cwd = ""

-- Store the original Status:name function
local original_status_name = Status.name

function Status:name()
    local cwd = tostring(cx.active.current.cwd)
    
    -- Send OSC7 when directory changes
    if cwd ~= old_cwd then
        local osc7 = string.format('\027]7;%s\027\\', cwd)
        
        local tty = io.open("/dev/tty", "w")
        if tty then
            tty:write(osc7)
            tty:flush()
            tty:close()
        end
        
        old_cwd = cwd
    end
    
    -- Call the original function if it exists, otherwise return empty
    if original_status_name then
        return original_status_name(self)
    else
        return ui.Line("")
    end
end
