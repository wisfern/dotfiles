#dotfiles

##注意事项

首先，更新所有submodule:

    $ git submodule update --init

如果需要强制建立软连接(以vim为例):

    $ make vim force=1

##vim

1. 系统依赖: ctags

2. 安装ctags:

    * Download ctags from <http://ctags.sourceforge.net/>
    * extract it, and

    ```
    $ ./configure
    $ sudo make install
    ```

3. then:

    ```
    $ make vim
    ```

##git

* [《Git Community Book 中文版》](http://gitbook.liuhui998.com/index.html)
* [《Git教程》](http://www.yiibai.com/git)
* 可以使用下面的命令初始化git配置环境
    
    ```shell
    $ make git
    ```
 
首先，更新所有submodule:

    $ git submodule update --init

如果需要强制建立软连接(以vim为例):

    $ make vim force=1

##vim

1. 系统依赖: ctags

2. 安装ctags:

    * Download ctags from <http://ctags.sourceforge.net/>
    * extract it, and

    ```
    $ ./configure
    $ sudo make install
    ```uu
##tmux

	* [zsh和oh-my-zsh安装与配置](https://blog.phpgao.com/oh-my-zsh.html)

    $ make tmux

##zsh

* [zsh和oh-my-zsh安装与配置](https://blog.phpgao.com/oh-my-zsh.html)

	$ make zsh

##bash

    $ make bash
	
##python
安装python3常用模块
	
	$ make python
	
python2则执行命令安装
	$ pip2 install -r python/requirements.txt

##reference

*最初阅读并参考了hit9的文章和dotfiles，特此表示感谢*

