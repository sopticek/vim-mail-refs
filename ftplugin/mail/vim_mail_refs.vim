if !has('python3') || exists('loaded_vim_mail_refs')
	finish
endif

python3 import sys
python3 import vim
python3 sys.path.append(vim.eval('expand("<sfile>:h")'))
python3 import vim_mail_refs

function! AddMailRef()
let ref_url = input('Enter URL: ')

python3 << END
vim_mail_refs.add_ref(
	vim.current.buffer,
	vim.current.window,
	vim.eval('l:ref_url')
)
END

endfunction

command! AddMailRef call AddMailRef()

let loaded_vim_mail_refs = 1
