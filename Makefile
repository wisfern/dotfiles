# vim:set noet: 
.PHONY : vim ssh git tmux

LNSOPT=-s

ifdef force
	ifeq ($(force),1)
		LNSOPT=-fs
	endif
endif

all:ssh git tmux vim

submodule:
	git submodule update --init

vim:submodule
	cd vim/vundle ; git checkout master ; git pull;
	mkdir -p ~/.vim/bundle/ 
	ln $(LNSOPT) $(CURDIR)/vim/vimrc ~/.vimrc
	ln $(LNSOPT) $(CURDIR)/vim/vundle ~/.vim/bundle/vundle
	vim -c "BundleInstall"
	cd ~/.vim/bundle/YouCompleteMe ;  ./install.sh --clang-completer

ssh:
	ln $(LNSOPT) $(CURDIR)/ssh/config ~/.ssh/config

git:
	ln $(LNSOPT) $(CURDIR)/git/gitconfig ~/.gitconfig
	ln $(LNSOPT) $(CURDIR)/git/gitignore_global ~/.gitignore_global

tmux:
	ln $(LNSOPT) $(CURDIR)/tmux/tmux.conf ~/.tmux.conf
