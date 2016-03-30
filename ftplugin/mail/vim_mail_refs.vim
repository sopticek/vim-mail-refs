if !has('python3') || exists('loaded_vim_mail_refs')
	finish
endif


python3 import sys
python3 import vim
python3 sys.path.append(vim.eval('expand("<sfile>:h")'))
python3 import vim_mail_refs


function! GetCursorPosForPython()
	" Originally, vim.current.windows.cursor was used in Python code to get
	" cursor position. It returns (row, col) where row is the line number and
	" col is the *byte offset* on the current line. However, in Python, we need
	" the column number, not the byte offset.To get it, we obtain the virtual
	" column number, which is what we want. The only caveat is that we have to
	" first set 'tabstop' to 1 to ensure that a tab is counted as a single
	" character. After we obtain the column, we restore the original value of
	" 'tabstop'.
	let row = line('.')
	let old_tabstop = &tabstop
	set tabstop=1
	let col = virtcol('.')
	let &tabstop = old_tabstop
	return [row - 1, col - 1]
endfunction


function! SetCursorPosInVim(row, col)
	" We have to convert cursor position from Python to Vim. In Python, the
	" position is based on characters, but in Vim it is based on bytes. The
	" conversion of row is simple (it is just the Python row + 1). To convert
	" the column, we move to the beginning of the line and apply 'l' (move
	" right) col times.
	execute 'normal! ' . (a:row + 1) . 'G'
	execute 'normal! 0'
	execute 'normal! ' . a:col . 'l'
endfunction


function! AddMailRef()
	let ref_url = input('Enter URL: ')
	let [row, col] = GetCursorPosForPython()

python3 << END
row, col = vim_mail_refs.add_ref(
	vim.current.buffer,
	(int(vim.eval('l:row')), int(vim.eval('l:col'))),
	vim.eval('l:ref_url')
)
vim.command('let row = {}'.format(row))
vim.command('let col = {}'.format(col))
END

	call SetCursorPosInVim(row, col)
endfunction


function! FixMailRefs()
	let [row, col] = GetCursorPosForPython()

python3 << END
row, col = vim_mail_refs.fix_mail_refs(
	vim.current.buffer,
	(int(vim.eval('l:row')), int(vim.eval('l:col')))
)
vim.command('let row = {}'.format(row))
vim.command('let col = {}'.format(col))
END

	call SetCursorPosInVim(row, col)
endfunction


command! AddMailRef call AddMailRef()
command! FixMailRefs call FixMailRefs()

let loaded_vim_mail_refs = 1
