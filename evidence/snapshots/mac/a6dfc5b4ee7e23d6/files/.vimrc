" default settings go here
set nocompatible
filetype off        " do not detect filetype i am working with

set laststatus=2
set number          " set the line numbers
set encoding=utf-8
set tabstop=2       
set shiftwidth=2
set expandtab       " convert tabs to spaces
set softtabstop=2
set smartindent
"set hlsearch        " highlight my searches
set t_Co=256
set wildmenu
set colorcolumn=80
set noshowmode

colorscheme zaibatsu
syntax on

call plug#begin()
   " List your plugins here
   Plug 'itchyny/lightline.vim'
call plug#end()
