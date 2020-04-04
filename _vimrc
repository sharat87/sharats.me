set wildignore+=*/_site/*,*/node_modules/*

command -nargs=1 NewPost call <SID>NewPost(<q-args>)
function s:NewPost(slug) abort
	exe 'edit posts/' .. strftime('%Y-%m-%d-') .. a:slug .. '.md'
	let title = a:slug->substitute('\v-(.)', ' \U\1', 'g')->substitute('^.', '\U\0', '')
	call append(0, ['---', 'title: ' .. title, '---'])
endfunction

command! Build tab ter npx.cmd eleventy

command! Serve call <SID>LaunchServer()
nnoremap <silent> <Leader>s :Serve<CR>
fun s:LaunchServer() abort
	let nr = bufnr('make serve')
	if nr >= 0
		call job_stop(term_getjob(nr))
	endif
	tab terminal make serve
endfun
