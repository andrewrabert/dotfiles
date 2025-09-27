local M = {}

local function get_pipe_dir()
  return os.getenv("TMPDIR") or "/tmp"
end

local function get_pipe_path(topic, pid)
  return string.format("%s/fanpipe-%s-%s", get_pipe_dir(), topic, pid or "")
end

local function publish(topic, message)
  local pipe_dir = get_pipe_dir()
  local prefix = string.format("fanpipe-%s-", topic)

  local pipes = {}
  local handle = vim.loop.fs_scandir(pipe_dir)
  if handle then
    while true do
      local name, type = vim.loop.fs_scandir_next(handle)
      if not name then break end
      if (type == "file" or type == "fifo") and name:sub(1, #prefix) == prefix then
        table.insert(pipes, pipe_dir .. "/" .. name)
      end
    end
  end

  if #pipes > 0 then
    local msg = message or ""
    for _, pipe in ipairs(pipes) do
      local f = io.open(pipe, "w")
      if f then
        f:write(msg)
        f:close()
      end
    end
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
