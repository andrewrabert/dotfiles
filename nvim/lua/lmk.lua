local M = {}

local function get_pipe_dir()
  return vim.uv.os_getenv("TMPDIR") or "/tmp"
end

local function get_pipe_path(topic, pid)
  return string.format("%s/fanpipe-%s-%s", get_pipe_dir(), topic, pid or "")
end

local function cleanup_stale_pipes(topic)
  local pipe_dir = get_pipe_dir()
  local prefix = string.format("fanpipe-%s-", topic)

  local handle = vim.uv.fs_scandir(pipe_dir)
  if not handle then return end

  while true do
    local name, type = vim.uv.fs_scandir_next(handle)
    if not name then break end
    if type == "fifo" and name:sub(1, #prefix) == prefix then
      local pid = name:match("fanpipe%-" .. topic .. "%-(%d+)")
      if pid then
        local pid_num = tonumber(pid)
        if pid_num then
          local success, err = vim.uv.kill(pid_num, 0)
          if not success or err then
            -- Process doesn't exist or kill failed
            os.remove(pipe_dir .. "/" .. name)
          end
        end
      end
    end
  end
end

local function publish(topic, message)
  cleanup_stale_pipes(topic)

  local pipe_dir = get_pipe_dir()
  local prefix = string.format("fanpipe-%s-", topic)

  local pipes = {}
  local handle = vim.uv.fs_scandir(pipe_dir)
  if handle then
    while true do
      local name, type = vim.uv.fs_scandir_next(handle)
      if not name then break end
      if type == "fifo" and name:sub(1, #prefix) == prefix then
        table.insert(pipes, pipe_dir .. "/" .. name)
      end
    end
  end

  if #pipes > 0 then
    local msg = message or ""
    local pipe_list = table.concat(pipes, " ")
    -- Use tee like fanpipe does - more efficient for multiple pipes
    vim.fn.jobstart(string.format("echo -n %q | tee %s > /dev/null", msg, pipe_list), {
      detach = true
    })
  end
end

function M.notify()
  publish('lmk', '')
end

function M.run(...)
  local args = {...}

  if #args == 0 then
    M.notify()
    return
  end

  M.notify()
end

return M
