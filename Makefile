# vim:set noet: 
.PHONY : vim ssh git tmux zsh bash

LNSOPT=-s

ifdef force
	ifeq ($(force),1)
		LNSOPT=-fs
	endif
endif

all:ssh git tmux zsh bash vim

submodule:
	git submodule update --init

vim:submodule
	cd vim/vundle ; git checkout master ; git pull;
	mkdir -p ~/.vim/bundle/ 
	ln $(LNSOPT) $(CURDIR)/vim/vimrc ~/.vimrc
	ln $(LNSOPT) $(CURDIR)/vim/vundle ~/.vim/bundle/
	vim +PluginInstall +qall
	#vim -c "BundleInstall"
	cd ~/.vim/bundle/YouCompleteMe ;  ./install.sh --clang-completer

ssh:
	ln $(LNSOPT) $(CURDIR)/ssh/config ~/.ssh/config

git:
	ln $(LNSOPT) $(CURDIR)/git/gitconfig ~/.gitconfig
	ln $(LNSOPT) $(CURDIR)/git/gitignore_global ~/.gitignore_global

tmux:
	ln $(LNSOPT) $(CURDIR)/tmux/tmux.conf ~/.tmux.conf

zsh:
	ln $(LNSOPT) $(CURDIR)/zsh/zshrc ~/.zshrc
	wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O - | sh
	chsh -s `which zsh`
	upgrade_oh_my_zsh

bash:
	ln $(LNSOPT) $(CURDIR)/bash/alias ~/.alias
	ln $(LNSOPT) $(CURDIR)/bash/function ~/.function
	ln $(LNSOPT) $(CURDIR)/bash/bashrc ~/.bashrc
	
python:
	pip install -r python/requirements.txt
