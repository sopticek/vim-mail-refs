python3 import sys
python3 import vim
python3 sys.path.append(vim.eval('expand("<sfile>:h")'))
python3 import vim_mail_refs

function! AddMailRef()
python3 << END
ref_url = ""
vim_mail_refs.add_ref(
	vim.current.buffer,
	vim.current.window,
	ref_url
)
END
endfunction

command! AddMailRef call AddMailRef()
