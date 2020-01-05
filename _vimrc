nnoremap <Leader>e :vertical terminal python manage.py build<CR>
set wildignore+=*/output/*

aug sharats_me
	au!
	au FileType markdown set ai sts=4
aug END
