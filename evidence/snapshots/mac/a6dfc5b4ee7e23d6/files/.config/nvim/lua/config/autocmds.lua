-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
--
-- Add any additional autocmds here
-- with `vim.api.nvim_create_autocmd`
--
-- Or remove existing autocmds by their group name (which is prefixed with `lazyvim_` for the defaults)
-- e.g. vim.api.nvim_del_augroup_by_name("lazyvim_wrap_spell")

vim.api.nvim_create_autocmd({ "BufWinEnter", "FileType" }, {
  desc = "Show invisible characters only in normal editable buffers",
  callback = function(args)
    local bt = vim.bo[args.buf].buftype
    local ft = vim.bo[args.buf].filetype

    local excluded_filetypes = {
      "lazy",
      "mason",
      "neo-tree",
      "snacks_dashboard",
      "Trouble",
      "help",
      "qf",
    }

    if bt == "" and not vim.tbl_contains(excluded_filetypes, ft) then
      vim.opt_local.list = true
    else
      vim.opt_local.list = false
    end
  end,
})

local function set_help_window_highlights()
  vim.api.nvim_set_hl(0, "HelpWindow", { bg = "#1f2335" })
  vim.api.nvim_set_hl(0, "HelpWindowNC", { bg = "#1a1d2b" })
end

vim.api.nvim_create_autocmd("ColorScheme", {
  callback = set_help_window_highlights,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = "help",
  callback = function()
    set_help_window_highlights()
    vim.opt_local.winhighlight = "Normal:HelpWindow,NormalNC:HelpWindowNC"
  end,
})

set_help_window_highlights()
