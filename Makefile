# vim:set noet: 
.PHONY : vim ssh git tmux zsh bash pip

LNSOPT=-s

ifdef force
	ifeq ($(force),1)
		LNSOPT=-fs
	endif
endif

all:ssh git tmux zsh bash vim pip

submodule:
	git submodule update --init

vim:submodule
	cd vim/k-vim ; git checkout master ; git pull;
	sh install.sh --for-vim
	ln $(LNSOPT) $(CURDIR)/vim/gtags.conf ~/.gtags.conf
	#cd vim/vundle ; git checkout master ; git pull;
	#mkdir -p ~/.vim/bundle/ 
	#ln $(LNSOPT) $(CURDIR)/vim/vimrc ~/.vimrc
	#ln $(LNSOPT) $(CURDIR)/vim/vundle ~/.vim/bundle/
	#vim +PluginInstall +qall
	#vim -c "BundleInstall"
	#cd ~/.vim/bundle/YouCompleteMe ;  ./install.sh --clang-completer

ssh:
	ln $(LNSOPT) $(CURDIR)/ssh/config ~/.ssh/config

git:
	ln $(LNSOPT) $(CURDIR)/git/gitconfig ~/.gitconfig
	ln $(LNSOPT) $(CURDIR)/git/gitignore_global ~/.gitignore_global

tmux:
	ln $(LNSOPT) $(CURDIR)/tmux/tmux.conf ~/.tmux.conf

zsh:
	wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O - | sh
	echo "请运行命令自行变更shell程序 chsh -s `which zsh`"
	#upgrade_oh_my_zsh
	ln $(LNSOPT) $(CURDIR)/zsh/zshrc ~/.zshrc
	ln $(LNSOPT) $(CURDIR)/zsh/function ~/.function

bash:
	ln $(LNSOPT) $(CURDIR)/bash/alias ~/.alias
	ln $(LNSOPT) $(CURDIR)/bash/function ~/.function
	ln $(LNSOPT) $(CURDIR)/bash/bashrc ~/.bashrc

python:
	pip install -r python/requirements.txt

gto:
	ln $(LNSOPT) $(CURDIR)/python/gto.py ~/.local/bin/gto

pip:
	mkdir -p ~/.config/pip
	ln $(LNSOPT) $(CURDIR)/pip/pip.conf ~/.config/pip/pip.conf
	# pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
	# pip config set install.trusted-host pypi.douban.com
