#!/home/devis/.local/share/virtualenvs/gto-eLTPUmZa/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import pexpect
import yaml
import signal
import shutil
from pexpect import pxssh
import logging
logging.basicConfig(level=logging.INFO,
                    format="%(level)s %(message)s")


def get_terminal_dimensions():
    columns, lines = shutil.get_terminal_size()
    return lines, columns


def register_winch_hander(app):
    # for resize windows
    def sigwinch_passthrough(sig, data):
        if app.expect:
            app.expect.setwinsize(*get_terminal_dimensions())

    sigwinch_passthrough(None, None)
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)


class Config(dict):
    def load_from_yaml(self, yaml_file):
        """
        load conf from yaml file
        :param yaml_file: yaml config file path
        """
        if not os.path.exists(yaml_file):
            logging.error("%s 路由文件不存在" % yaml_file)
            return
        with open(yaml_file) as file_obj:
            conf = yaml.load(file_obj.read())
            self.from_mapping(conf)

    def from_mapping(self, *mapping, **kwargs):
        """
        Updates the config like :meth:`update`
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError('expected at most 1 positional argument, got %d' %
                            len(mapping))
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                self[key] = value

        return True

    def get_route(self, target):
        try:
            if target == "local":
                return None
            else:
                return self['route'][target]
        except KeyError as e:
            if e == 'route':
                print("have not avalid route, please check your config file.")
                sys.exit(3)
            else:
                raise e

    def get_host(self, target):
        try:
            if target == "local":
                return None
            else:
                return self['host'][target]
        except KeyError as e:
            if e == 'host':
                print("have not avalid hosts, please check your config file.")
                sys.exit(2)
            else:
                raise e

    def _merge_route(self, route_left, route_right):
        """
        由left合并right路径，并保留最后一个重复出现的节点
        left = [1,2,3,9]
        right = [1, 3, 5, 8]
        return [8, 5, 3, 9]
        """
        if not route_right:
            return []
        host_count = {k: 1 for k in route_right}
        for id, host in enumerate(route_left):
            if 0 == host_count.get(host, 0):
                host = route_left[id - 1]
                break
            else:
                continue
        else:
            id += 1
        # print("debug", id, host, list(reversed(route_left[id:])), route_right.index(host))
        return list(reversed(route_left[id:])) + route_right[route_right.index(host):], host

    def local_to_target_route(self, target):
        try:
            if target == "local":
                return [target]
            else:
                node = self.get_route(target)[0]
                return self.local_to_target_route(node) + [target]
        except KeyError as e:
            logging.error("此主机没有配置路由 {}".format(target))
            raise

    def generate_target_route(self, target, source='local'):
        try:
            local_to_source = self.local_to_target_route(source)
            local_to_target = self.local_to_target_route(target)
            return self._merge_route(local_to_source, local_to_target)
        except KeyError as e:
            sys.exit(2)
        except Exception as e:
            print(type(e), e)
            raise e

    def show_routes(self):
        for one in self['route'].keys():
            print('{}: {}'.format(one, ' => '.join(self.local_to_target_route(one))))

    def show_hosts(self):
        print("#alias    ip-port-user")
        for key, one in self['host'].items():
            print("{}   {}-{}-{}".format(key, one[0], one[1], one[2]))


# TODO: 包装ssh命令
# 重写login, 由一个栈记录登陆层次
# 用expect对象是否为None来确定用sendline还是用_spawn
class OpSsh(pxssh.pxssh):
    def __init__():
        pass


# TODO: 包装scp命令
class OpScp(object):
    def get():
        """
        从远端主机获取文件到指定的路径
        """
        pass

    def put():
        """
        把本机指定路径的文件传输到远端指定的路径
        """
        pass


class Gto(object):
    def __init__(self):
        self.config = Config()
        self.expect = None
        self.debug = 0
        self.login_path = []
        if os.path.exists("/etc/knowhosts.yml"):
            self.config.load_from_yaml("/etc/knowhosts.yml")
        private_conf_path = os.environ['HOME'] + "/.knowhosts.yml"
        if os.path.exists(private_conf_path):
            self.config.load_from_yaml(private_conf_path)

    def _print_debug(self, lineno=None):
        if self.debug and self.debug >= 2:
            print("")
            print('=' * 30 + 'debug {}'.format(lineno) + '=' * 30)
            print("before [{} *]".format(self.expect.before))
            print("after [{}]".format(self.expect.after))
            print("buffer [{} *]".format(self.expect.buffer))
            print("match [{}]".format(self.expect.match))
            # print(str(self.expect))
            print('=' * 30 + ' end ' + '=' * 30)

    def ssh_command(self, host, port, user, password, command, option_list=[], expect_login_after="-"):
        """
        # user: ssh 主机的用户名
        # host：ssh 主机的域名
        # password：ssh 主机的密码
        # command：即将在远端 ssh 主机上运行的命令
        """
        ssh_newkey = r'Are you sure you want to continue connecting'
        password_regex = r'(?i)(?:password:)|(?:passphrase for key)'
        permission_regex = r'(?i)permission denied'
        # prompt = r'[#$]'  # 要匹配终端提示符，需要在expect之前清空了buffer
        prompt = r'abcd@#$%'  # 禁用提示符匹配
        session_regex_array = [ssh_newkey, password_regex, expect_login_after, prompt, permission_regex, pexpect.TIMEOUT, pexpect.EOF]

        # 为 ssh 命令生成一个 spawn 类的子程序对象.
        ssh = " -o ".join(["ssh -l {user} {host} -p {port}".format(**locals())] + option_list)
        self.expect.buffer = ""
        self.expect.sendline(ssh)
        i = self.expect.expect(session_regex_array)
        if i == 0:
            self.expect.buffer = ""
            self.expect.sendline("yes")
            i = self.expect.expect(session_regex_array)
        if i == 1:  # password or passphrase
            self.expect.buffer = ""
            self.expect.sendline(password)
            i = self.expect.expect(session_regex_array)
        if i == 5:  # Timeout
            self._print_debug()
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print("before [{}] \nafter [{}]".format(self.expect.before, self.expect.after))
            self.expect.close(force=True)
            raise TimeoutError('SSH Timeout [{}]'.format(ssh))
        if i == 6:  # EOF
            self._print_debug()
            self.expect.close()
            raise RuntimeError('Could not establish connection to host')

        # 可能出现密码错误
        if i == 0:
            self.expect.close()
            raise RuntimeError('Weird error. Got "are you sure" prompt twice.')
        elif i == 1:  # password prompt again
            self.expect.close()
            raise RuntimeError('password refused')
        elif i == 2:  # 登陆后所期望的输出
            pass
        elif i == 3:  # prompt
            self._print_debug()
            pass
        elif i == 4:  # permission denied -- password was bad.
            self.expect.close()
            raise RuntimeError('permission denied')
        else:
            print("login [{}] success".format(ssh))

        if command:
            self.expect.buffer = ""
            self.expect.sendline(command)
            i = self.expect.expect(session_regex_array)
            self._print_debug()

        return expect_login_after

    def ssh_logout(self):
        '''Sends exit to the remote shell.
        If there are stopped jobs then this automatically sends exit twice.
        '''
        self.expect.sendline("exit")
        index = self.expect.expect([pexpect.EOF, pexpect.TIMEOUT, "(?i)there are stopped jobs"], timeout=1)
        if index == 2:
            self.sendline("exit")
        exited_host = self.login_path.pop()
        if self.debug >= 1:
            print("{} exit!".format(exited_host))

    def ssh_login(self, host):
        # 登陆到指定的机器，如果为local则，新建expect对象
        focus = '$'
        if host == "local":
            self.expect = pexpect.spawn('bash', encoding='utf8')
            register_winch_hander(self)
            if self.debug and self.debug >= 1:
                fout = open("/tmp/gto.log", 'w')
                self.expect.logfile = fout
            self.expect.logfile_read = sys.stdout
            self.login_path.append(host)
        else:
            host_info = self.config.get_host(host)
            logging.debug("host_info = {}".format(host_info))
            if not host_info[6]:
                options = []
            else:
                options = host_info[6].split(";")
            focus = self.ssh_command(host_info[0], host_info[1], host_info[2],
                                     host_info[3], host_info[7], options, host_info[5])
        self.login_path.append(host)
        return focus

    def generate_target_route(self, target, source='local'):
        return self.config.generate_target_route(target, source)

    def login_to(self, target):
        ru, _ = self.generate_target_route(target)
        focus = "$"
        for node in ru:
            focus = self.ssh_login(node)
        return focus

    def __call__(self, target):
        self.login_to(target)

        # 归还终端
        # self.expect.sendcontrol('c')
        self.expect.send(self.expect.linesep)
        self.expect.logfile_read = None
        self.expect.interact()

    def scp_file(self, source, target):
        scp_source_d, scp_target_d = self._init_scp_inf(source, target)
        s_d_ru, transit = self.generate_target_route(scp_target_d['d_host'], scp_source_d['s_host'])
        # 登陆到中转机
        focus = self.login_to(transit)

        try:
            # 从源主机获取文件，递归方法
            get_ru, _ = self.generate_target_route(scp_source_d['s_host'], transit)
            self._x_get_file_from_source(get_ru, scp_source_d['s_host']
                                         , scp_source_d['s_path']
                                         , scp_source_d['s_file']
                                         , scp_target_d['d_path'] if transit == s_d_ru[-1] else '/tmp'
                                         , focus)

            # 把文件发送目标主机，递归方法
            put_ru, _ = self.generate_target_route(scp_target_d['d_host'], transit)
            self._x_put_file_to_target(put_ru[1:], scp_target_d['d_host']
                                       , scp_target_d['d_path']
                                       , scp_target_d['d_file']
                                       , scp_source_d['s_path'] if transit == s_d_ru[-1] else '/tmp'
                                       , focus)
            # TODO: 如果非两端机，还得清理一下中间数据
        except Exception as e:
            logging.error("[{}] => [{}] error: {}".format(source, target, e))
            return False
        else:
            # 完成文件传输
            if self.debug >= 1:
                print("scp get rule {}".format(get_ru))
                print("scp put rule {}".format(put_ru))
            print("[{}] => [{}] done!".format(source, target))
            return True

    def _x_get_file_from_source(self, ru, source_host, source_path, file_name, target_path='/tmp/', focus='$'):
        """
        把文件从源路径传送到目标路径
        :param ru: 目标路由 [source, ..., target]
        :param source_host: 传进来的值应该等于路由里面的最后一项
        """
        if not ru or len(ru) <= 1:
            return True

        if ru[1] != source_host:
            new_focus = self.ssh_login(ru[1])    # 登陆到第一台机
            self._x_get_file_from_source(ru[1:], source_host, source_path, file_name, '/tmp', new_focus)
            self.ssh_logout()
        else:
            logging.debug("get op, but next host == source {}".format(source_host))

        # 把下一台机的文件scp过来到本机
        scp_source_path = source_path if ru[1] == source_host else '/tmp'
        host_src = self.config.get_host(ru[1])
        scp_cmd = "scp -P {port} {user}@{ip}:{scp_source_path}/{file_name} {target_path}/{file_name} ;".format(
            port=host_src[1], user=host_src[2], ip=host_src[0], **locals()
        )
        scp_nospace_left_err = 'No space left on device'
        cmd = scp_cmd
        for inum in range(2):
            self.expect.buffer = ""
            self.expect.sendline(cmd)
            i = self.expect.expect([host_src[5], '(?i)password', r'100%', scp_nospace_left_err, pexpect.TIMEOUT, pexpect.EOF], timeout=None)
            if i == 1 and inum == 0:
                cmd = host_src[3]
                continue
            elif i == 1 and inum == 1:
                error = "host [{}-{}-{}] password error!".format(host_src[0], host_src[1], host_src[2])
                raise PermissionError(error)
            elif i in [0, 2]:
                # TODO: 如果非两端机，还得清理一下中间数据
                return True
            elif i == 3:
                raise RuntimeError("{} error: {}".format(scp_cmd, scp_nospace_left_err))
            else:
                print("get file error! [{}] index[{}]".format(scp_cmd, i))
                return False

    def _x_put_file_to_target(self, ru, target_host, target_path, file_name, source_path='/tmp/', focus='$'):
        """
        :param ru: 目标路由 [source, ..., target]
        """
        if not ru:
            return True

        # 目标机
        scp_target_path = target_path if ru[0] == target_host else '/tmp'
        host_src = self.config.get_host(ru[0])
        scp_cmd = "scp -P {port} {source_path}/{file_name} {user}@{ip}:{scp_target_path}/{file_name}".format(
            port=host_src[1]
            , user=host_src[2]
            , ip=host_src[0]
            , **locals()
        )
        scp_nospace_left_err = 'No space left on device'
        cmd = scp_cmd
        for inum in range(2):
            self.expect.buffer = ""
            self.expect.sendline(cmd)
            i = self.expect.expect([host_src[5], '(?i)password', '100%', scp_nospace_left_err, pexpect.TIMEOUT, pexpect.EOF], timeout=None)
            if i == 1 and inum == 0:
                cmd = host_src[3]
                continue
            elif i == 1 and inum == 1:
                error = "host [{}-{}-{}] password error!".format(
                    host_src[0], host_src[1], host_src[2]
                )
                raise PermissionError(error)
            elif i in [0, 2]:
                if ru[0] != target_host:
                    new_focus = self.ssh_login(ru[0])
                    self._x_put_file_to_target(ru[1:], target_host, target_path, file_name, '/tmp', new_focus)
                    self.ssh_logout()  # 输出 ru[0]
                # TODO: 如果非两端机，还得清理一下中间数据
                return True
            elif i == 3:
                raise RuntimeError("{} error: {}".format(scp_cmd, scp_nospace_left_err))
            else:
                print("put file error! [{}] index[{}]".format(cmd, i))
                return False

    def _init_scp_inf(self, source, target):
        """
        :param source: 源文件路径  xxx:xxxx
        :param target: 目标文件路径  xxx:xxx
        """
        if ':' in source:
            s_host, abs_path = source.split(':')
            s_path = os.path.dirname(abs_path)
            s_file = os.path.basename(abs_path)
        else:
            s_host = 'local'
            s_path = os.path.dirname(source)
            s_file = os.path.basename(source)

        if ':' in target:
            d_host, abs_path = target.split(':')
            d_path = os.path.dirname(abs_path)
            d_file = os.path.basename(abs_path)
        else:
            d_host = 'local'
            d_path = os.path.dirname(target)
            d_file = os.path.basename(target)

        return {'s_host': s_host, 's_path': s_path, 's_file': s_file}, {'d_host': d_host, 'd_path': d_path, 'd_file': d_file}


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='gto'
        , formatter_class=argparse.RawDescriptionHelpFormatter
        , description='gto tools with ssh、scp')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('lflag', action='store', nargs='?', help='host or alias need to login')
    parser.add_argument('-showhosts', action='store_true', help='show all host config.')
    parser.add_argument('-showroute', action='store_true', help='show route config.')
    parser.add_argument('-scp', metavar=('source', 'target'), action='store', nargs=2, help='scp file from source to target')
    parser.epilog = """Example:
  %(prog)s lflag  登陆lflag机
  %(prog)s -scp sourcehost:abs_file_path  targethost:abs_file_path  把文件由sourcehost传输到targethost
    """
    args = parser.parse_args()

    gto = Gto()
    gto.debug = args.verbose
    if args.showhosts:
        gto.config.show_hosts()
        exit(0)
    elif args.showroute:
        gto.config.show_routes()
    elif args.scp:
        gto.scp_file(*args.scp)
    elif args.lflag:
        gto(args.lflag)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        pass
    # import trace

    # create a Trace object, telling it what to ignore, and whether to
    # do tracing or line-counting or both.
    # tracer = trace.Trace(
        # ignoredirs=[sys.prefix, sys.exec_prefix],
        # trace=0,
        # count=1)

    # run the new command using the given tracer
    # tracer.run('main()')

    # make a report, placing output in the current directory
    # r = tracer.results()
    # save_path = os.path.dirname(__file__)
    # r.write_results(show_missing=True, coverdir=save_path if save_path else '.')
