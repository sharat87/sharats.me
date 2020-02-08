set wildignore+=*/output/*,*.iml,.idea/*

command -nargs=1 NewPost call <SID>NewPost(<q-args>)
function s:NewPost(slug) abort
	exe 'edit content/posts/' .. strftime('%Y-%m-%d_') .. a:slug .. '.md'
	let title = a:slug->substitute('\v-(.)', ' \U\1', 'g')->substitute('^.', '\U\0', '')
	call append(0, ['---', 'title: ' .. title, '---'])
endfunction

aug sharats_me
	au!
	au FileType markdown set ai sts=4
aug END
