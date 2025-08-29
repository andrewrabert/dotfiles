set autoread

autocmd InsertLeave,TextChanged,FocusLost,BufLeave * :update
autocmd FocusGained,BufEnter * :checktime

" talbe_mode_always_active breaks highlighting
TableModeEnable

let g:vim_markdown_auto_insert_bullets=1
let g:vim_markdown_new_list_item_indent=0
setlocal formatlistpat=^\\s*\\d\\+[.\)]\\s\\+\\\|^\\s*[*+~-]\\s\\+\\\|^\\(\\\|[*#]\\)\\[^[^\\]]\\+\\]:\\s 
setlocal comments=n:>
setlocal formatoptions+=cn
nnoremap <leader>m 0:TableModeRealign<Cr>
set linebreak
set list& listchars&
highlight Title cterm=bold

let g:vim_markdown_conceal_code_blocks = 0

let g:vim_markdown_folding_style_pythonic = 1
let g:vim_markdown_folding_level = 6
let g:vim_markdown_folding_disabled = 1


" r Automatically insert the current comment leader after hitting
"   <Enter> in Insert mode.
" o Automatically insert the current comment leader after hitting 'o' or
"   'O' in Normal mode.
set formatoptions+=ro

" markdown folds are horrendouly fucked in neovim.
" bullshit automatic closing of other folds when doing `c$` on heading level 3, probably others
set nofoldenable

function! SortByDataviewDate(date_type) range
    let date_types = empty(a:date_type) ? ['due', 'scheduled', 'start'] : [a:date_type]
    
    let line_dates = []
    for line in getline(a:firstline, a:lastline)
        let date = '9999-99-99'
        for type in date_types
            let match = matchstr(line, '\[' . type . '::\s*\zs\d\d\d\d-\d\d-\d\d\ze\]')
            if !empty(match)
                let date = match | break
            endif
        endfor
        call add(line_dates, [line, date])
    endfor
    
    call sort(line_dates, {a, b -> a[1] > b[1] ? 1 : a[1] < b[1] ? -1 : 0})
    call setline(a:firstline, map(line_dates, 'v:val[0]'))
endfunction

command! -range -nargs=? SortByDate <line1>,<line2>call SortByDataviewDate(<q-args>)
