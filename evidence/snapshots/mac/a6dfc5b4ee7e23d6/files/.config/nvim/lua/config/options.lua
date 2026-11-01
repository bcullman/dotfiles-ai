-- Add any additional options here
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Options are automatically loaded before lazy.nvim startup

vim.opt.conceallevel = 0
vim.opt.list = false
vim.opt.listchars = { tab = "» ", trail = "·", nbsp = "␣", space = "·" }
vim.opt.relativenumber = false
vim.opt.virtualedit = "onemore"
vim.opt.whichwrap:append("<,>,[,],h,l")
vim.opt_local.concealcursor = ""
