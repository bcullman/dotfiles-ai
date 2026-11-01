return {
  {
    "saghen/blink.cmp",
    opts = {
      keymap = {
        preset = "super-tab",

        -- optional, make Enter insert a newline instead of accepting completion
        ["<CR>"] = { "fallback" },
      },
    },
  },
}
