"
" Project:   vim-mail-refs
" Copyright: (c) 2016 by Daniela Ďuričeková <daniela.duricekova@protonmail.com>
"            and contributors
" License:   MIT, see the LICENSE file for more details
"

if !has('python3') || exists('loaded_vim_mail_refs')
	finish
endif


python3 import sys
python3 import vim
python3 sys.path.append(vim.eval('expand("<sfile>:h")'))
python3 import vim_mail_refs


function! s:GetCursorPosForPython()
	" Originally, vim.current.windows.cursor was used in Python code to get
	" cursor position. It returns (row, col) where row is the line number and
	" col is the *byte offset* on the current line. However, in Python, we need
	" the column number, not the byte offset.To get it, we obtain the virtual
	" column number, which is what we want. The only caveat is that we have to
	" first set 'tabstop' to 1 to ensure that a tab is counted as a single
	" character. After we obtain the column, we restore the original value of
	" 'tabstop'. We also need to disable 'linebreak' to ensure that
	" virtcol('.') returns a correct value.
	let row = line('.')
	let old_tabstop = &tabstop
	set tabstop=1
	let old_linebreak = &linebreak
	set nolinebreak
	let col = virtcol('.')
	let &linebreak = old_linebreak
	let &tabstop = old_tabstop
	return [row - 1, col - 1]
endfunction


function! s:SetCursorPosInVim(row, col)
	" We have to convert cursor position from Python to Vim. In Python, the
	" position is based on characters, but in Vim it is based on bytes. The
	" conversion of row is simple (it is just the Python row + 1). To convert
	" the column, we move to the beginning of the line and apply 'l' (move
	" right) col times.
	execute 'normal! ' . (a:row + 1) . 'G'
	execute 'normal! 0'
	execute 'normal! ' . a:col . 'l'
endfunction


function! s:AddMailRef()
	let ref_url = input('Enter URL: ')
	if ref_url != ''
		call s:AddMailRefOrUrl(ref_url)
	endif
endfunction


function! s:AddMailRefFromMenu()
	let ref = s:GetRefFromMenuWithRefsWithUrls()
	if ref != ''
		call s:AddMailRefOrUrl(ref)
	endif
endfunction


function! s:AddMailRefOrUrl(ref_or_url)
	let [row, col] = s:GetCursorPosForPython()

python3 << END
row, col = vim_mail_refs.add_ref(
	vim.current.buffer,
	(int(vim.eval('l:row')), int(vim.eval('l:col'))),
	vim.eval('a:ref_or_url')
)
vim.command('let row = {}'.format(row))
vim.command('let col = {}'.format(col))
END

	call s:SetCursorPosInVim(row, col)
endfunction


function! s:GetRefFromMenuWithRefsWithUrls()
python3 << END
refs_with_urls = vim_mail_refs.get_refs_with_urls_for_menu(
	vim.current.buffer
)
vim.command('let refs_with_urls = {}'.format(refs_with_urls))
END

	echohl Title
	echo 'Existing references:'
	echohl None
	for ref_with_url in refs_with_urls
		echo ref_with_url
	endfor
	echo ''
	let ref = input('Select reference: ')
	return ref
endfunction


function! s:FixMailRefs()
	let [row, col] = s:GetCursorPosForPython()

python3 << END
row, col = vim_mail_refs.fix_mail_refs(
	vim.current.buffer,
	(int(vim.eval('l:row')), int(vim.eval('l:col')))
)
vim.command('let row = {}'.format(row))
vim.command('let col = {}'.format(col))
END

	call s:SetCursorPosInVim(row, col)
endfunction


command! AddMailRef call s:AddMailRef()
command! AddMailRefFromMenu call s:AddMailRefFromMenu()
command! FixMailRefs call s:FixMailRefs()

let loaded_vim_mail_refs = 1
