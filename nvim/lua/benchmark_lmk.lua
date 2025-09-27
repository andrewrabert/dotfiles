local M = {}

local lmk = require('lmk')

local function benchmark(name, func, iterations)
  local start = vim.loop.hrtime()
  for i = 1, iterations do
    func()
  end
  local elapsed = (vim.loop.hrtime() - start) / 1e6  -- Convert to milliseconds
  print(string.format("%s: %.2fms total, %.4fms per call (%d iterations)",
        name, elapsed, elapsed / iterations, iterations))
end

function M.run(iterations)
  iterations = iterations or 1000
  print("Benchmarking lmk implementations:")

  -- Benchmark native Lua version
  benchmark("Lua lmk.notify()", function()
    lmk.notify()
  end, iterations)
end

-- Auto-run on require
M.run()

return M