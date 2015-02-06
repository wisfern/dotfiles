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

    $ make git
     
##tmux

    $ make tmux

##reference

*最初阅读并参考了hit9的文章和dotfiles，特此表示感谢*

