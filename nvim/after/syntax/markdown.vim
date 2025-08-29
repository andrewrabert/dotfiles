syntax case match

" due
syn match mkdDue /due:\d\d\d\d-\d\d-\d\d/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
hi def link mkdDue Todo

" date|est|goal|after
syn match mkdDate /\(date\|est\|goal\|after\):\d\d\d\d-\d\d-\d\d/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine,mkdLink
hi mkdDate cterm=bold ctermfg=6

" todo
syn match mkdTodo /TODO:\?/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine,mkdLink
hi def link mkdTodo Todo
hi Todo cterm=bold ctermfg=5

" checkbox
syn match mkdCheckboxUnchecked /\[ \]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
syn match mkdCheckboxChecked /\[x\].*/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
hi def mkdCheckboxUnchecked ctermfg=8
hi def mkdCheckboxChecked ctermfg=8

" Obsidian Tasks plugin dataview format
syn match mkdTaskDue /\[due::\s*\d\d\d\d-\d\d-\d\d\]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
syn match mkdTaskScheduled /\[scheduled::\s*\d\d\d\d-\d\d-\d\d\]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
syn match mkdTaskStart /\[start::\s*\d\d\d\d-\d\d-\d\d\]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
syn match mkdTaskCompletion /\[completion::\s*\d\d\d\d-\d\d-\d\d\]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
syn match mkdTaskPriority /\[priority::\s*\w\+\]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
syn match mkdTaskRepeat /\[repeat::\s*[^\]]\+\]/ containedin=htmlH[1-6],mkdNonListItemBlock,mkdListItemLine
hi def mkdTaskDue cterm=bold ctermfg=1
hi def mkdTaskScheduled cterm=bold ctermfg=3
hi def mkdTaskStart cterm=bold ctermfg=2
hi def mkdTaskCompletion cterm=bold ctermfg=2
hi def mkdTaskPriority cterm=bold ctermfg=5
hi def mkdTaskRepeat cterm=bold ctermfg=6

" bold and italics
hi mkdItalic        term=italic cterm=italic gui=italic
hi htmlBold         term=bold cterm=bold gui=bold
hi mkdBoldItalic    term=bold,italic cterm=bold,italic gui=bold,italic

" heading level colors
hi mkdHeading ctermfg=8

" purple
hi htmlH1 cterm=bold,underline ctermfg=5
" blue
hi htmlH2 cterm=bold ctermfg=4
" cyan
hi htmlH3 ctermfg=6
" yellow
hi htmlH4 ctermfg=11
" orange
hi htmlH5 ctermfg=16
" red
hi htmlH6 ctermfg=1

hi mkdURL ctermfg=8
syntax case ignore
