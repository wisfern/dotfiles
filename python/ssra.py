# -*- coding: utf-8 -*-
# Author: Wisfern
# Create Date: 2018-06-15
# 运行方法，在root用户下，并cd到ssr安装目录，同级目录有一个config.json文件
# pip3 install requests[socks] prettytable
# python3 ssa.py
import base64
import json
import logging
import multiprocessing
import os
import re
import subprocess
import time
from urllib import parse

import requests
from prettytable import PrettyTable
from pymongo import MongoClient

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s %(message)s', level=logging.INFO)

config = {
    'sub_urls': [
        'https://yzzz.ml/freessr/',
        'https://raw.githubusercontent.com/ImLaoD/sub/master/ssrshare.com'
    ],
    'url_list': [
        'ssr://MTY1LjIyNy42Mi4xODI6MTkwMjA6b3JpZ2luOnJjNC1tZDU6cGxhaW46Y0dGemN6a3dNakEvP29iZnNwYXJhbT0mcmVtYXJrcz02WUM0NVllaA',
    ],
    'test_latency_urls': [
        # "https://www.google.com",
        # "https://twitter.com",
        # "http://ifconfig.me/ip",
        "https://api.lbank.info",
        # "https://data.gate.io/api2/1/public"
    ],
    'ssr_config': {},  # {'ip:port': ssr_config_dict}
    # 'ssr_bin': 'shadowsocks/shadowsocks-local.exe'
    'ssr_bin': 'shadowsocks/local.py',
    'target_config': 'config.json',
    'parallet': 30,
    'proxies': {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    },
    'mongo': {
        'host': '172.16.1.13',
        'port': 27017
    }
}


def load_ssr_from_mongo():
    mc = MongoClient(**config['mongo'])
    mc.server_info()
    ssr_db = mc['ssr']
    ssr_coll = ssr_db['config']
    cursor = ssr_coll.find({})
    if cursor:
        return list(cursor)
    else:
        return []


def dump_ssr_to_mongo(ssr_config_list):
    """
    保存ssr配置列表到mongo
    :param ssr_config_list:
    :return:
    """
    mc = MongoClient(**config['mongo'])
    mc.server_info()
    ssr_db = mc['ssr']
    ssr_coll = ssr_db['config']
    for one in ssr_config_list:
        ssr_coll.replace_one({'server': one['server'], 'server_port': one['server_port']}, one, upsert=True)


def parseSub(sub_url):
    logging.info("get sub url[{}] text...".format(sub_url))
    try:
        data = requests.get(sub_url, proxies=config['proxies'], timeout=10)
        if data and data.status_code == 200:
            return str(base64.standard_b64decode(data.text), encoding="utf-8")
            # return base64.urlsafe_b64decode(data.text)
    except Exception as e:
        return ""


def b64decode(b64str):
    """自动补全结尾的=号"""
    missing_padding = 4 - len(b64str) % 4
    if missing_padding:
        b64str += '=' * missing_padding
    return str(base64.urlsafe_b64decode(b64str), encoding="utf-8")


def parse_b64ssr_to_dict(ssr_url):
    ssr64 = one_ssr_url[6:].rstrip()
    ssr = b64decode(ssr64)

    # ssr://server:port:protocol:method:obfs:password_base64/?obfsparam=obfsparam_base64&protoparam=protoparam_base64&remarks=remarks_base64&group=group_base64
    pattern = re.compile(
        r"(?P<server>.*?):(?P<port>.*?):(?P<protocol>.*?):(?P<method>.*?):(?P<obfs>.*?):(?P<b64password>.*?)/\?(?P<urlparam>.*)"
    )
    match = re.match(pattern, ssr.replace(" ", ""))
    if match:
        smethod = match.group("method")
        spassword = match.group("b64password")
        sprotocol = match.group("protocol")
        sobfs = match.group("obfs")
        sserver = match.group("server")
        sserver_port = match.group("port")
        urlparam = match.group("urlparam")
        url_param_dict = dict(parse.parse_qsl(urlparam))
        sb64obfsparam = url_param_dict.get("obfsparam", "").replace(' ', '+')
        sb64protoparam = url_param_dict.get("protoparam", "").replace(' ', '+')
        sb64remarks = url_param_dict.get("remarks", "").replace(' ', '+')
        sb64group = url_param_dict.get("group", "").replace(' ', '+')

        ssr_url_dict = dict(
            server=sserver,
            server_port=int(sserver_port),
            password=b64decode(spassword),
            method=smethod,
            protocol=sprotocol,
            protocol_param=b64decode(sb64protoparam),
            obfs=sobfs,
            obfs_param=b64decode(sb64obfsparam),
            remarks=b64decode(sb64remarks),
            group=b64decode(sb64group)
        )
        return ssr_url_dict
    else:
        return dict()


def update_ssr_config(ssr_config, to=None):
    """
    更新ssr客户端正式配置文件
    :param ssr_config:
    :type ssr_config: dict
    :param to: ssr客户端文件路径
    :return:
    """
    if not to:
        to = "config.json"

    with open(to) as file:
        raw_ssr_conf = json.loads(file.read())

    # ssr_config = json.loads(ssr_config_json)
    del ssr_config['latency']
    del ssr_config['ssr_url']
    raw_ssr_conf.update(ssr_config)
    with open(to, "w", encoding="utf-8") as fileto:
        json.dump(raw_ssr_conf, fileto, indent=4)


# 获取延迟数据函数组
def get_latency(url):
    logging.debug("test the latency of " + url + "...")
    for i in range(3):
        try:
            start = time.time()
            # r = request.urlopen(url, timeout=5)
            requests.get(url, timeout=10)
            end = time.time()
            latency = end - start
            logging.debug("the latency of " + url + " is " + str(latency))
            return latency
        except requests.exceptions.ConnectionError as e:
            if i >= 3:
                logging.error("this socks proxy may be invalid, {}".format(e))
        except requests.exceptions.ReadTimeout as e:
            break
        except Exception as e:
            logging.error("this socks proxy may be invalid, {} {}".format(type(e), e))
            break

    return 10  # 已经是无效的ssr了


def get_average_latency():
    urls = config['test_latency_urls']
    latencysum = 0
    for url in urls:
        latencysum += get_latency(url)
    averagelatency = latencysum / len(urls)
    logging.debug("the average latency is " + str(averagelatency))
    return averagelatency


# 延迟测试进程
def get_latency_of_proxy(ssr_config, process='0'):
    """
    针对一个ssr代理配置开一条进程测试代理延迟
    :param ssr_config: ssr配置
    :type ssr_config: dict
    :return:
    """
    import socks
    import socket

    def create_connection(address, timeout=None, source_address=None):
        # 因为socket模块中的create_connection在建立socket之前使用getaddrinfo查询DNS，很容易受到GFW的污染，因此需要在这里自定义create_connect
        # 把原来的sock替换为我们导入的模块中的socks.socksocket()，让它来接管DNS查询、连接等后续操作，最后返回可用的socket就可以了
        sock = socks.socksocket()
        sock.connect(address)
        return sock

    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", ssr_config['local_port'])
    # socket.setdefaulttimeout(20.0)
    socket.socket = socks.socksocket
    socket.create_connection = create_connection

    config_filename = '.'.join(['_'.join(["config", str(ssr_config['local_port'])]), "json"])
    ssr_config_json = json.dumps(ssr_config)
    logging.debug("Testing %s " % process + ssr_config_json + " ...")
    try:
        # 设置config.json文件
        f = open("shadowsocks/%s" % config_filename, "w")
        f.write(ssr_config_json)
        f.close()
        # 启动shadowsocks代理程序
        # cmd = ["shadowsocks/shadowsocks-local.exe","-c","shadowsocks/config.json"]
        cmd = [config['ssr_bin'], "-c", "shadowsocks/%s" % config_filename]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        a = get_average_latency()
        p.kill()
        time.sleep(0.5)
        ssr_config['latency'] = a
        ssr_config['local_port'] = 1080
        os.unlink("shadowsocks/%s" % config_filename)
        logging.info("process {} {}:{} latency is {}".format(
            process, ssr_config['server'], ssr_config['server_port'], a
        ))
        return ssr_config
    except Exception as e:
        logging.error("get_latency_of_proxy error = %s" % e)
        return (10, ssr_config)


if __name__ == "__main__":
    ssr_list = []  # 保存ssr解析后的配置
    ssr_url_list = config['url_list']  # 保存ssr://协议
    for one_ssr_sub in config['sub_urls']:
        data = parseSub(one_ssr_sub)
        ssr_url_list = list(set(data.split('\n')) | set(ssr_url_list))
    logging.info("get {} ssr url from suburl{}".format(len(ssr_url_list), config['sub_urls']))

    # 从数据库中加载配置
    if config['mongo']:
        config_in_db = load_ssr_from_mongo()
        for one in config_in_db:
            config['ssr_config'].update({
                '{}:{}'.format(one['server'], one['server_port']): one
                for one in config_in_db
            })
        ssr_url_list = list(set([one['ssr_url'] for one in config_in_db]) | set(ssr_url_list))
        logging.info('load {} ssr config from db'.format(len(config_in_db)))

    # 转换ssr_url为ssr配置字典
    for one_ssr_url in ssr_url_list:
        if not one_ssr_url: continue
        ssr_config = parse_b64ssr_to_dict(one_ssr_url)
        if ssr_config:
            ssr_config.update(dict(
                local_port=1080,
                timeout=600,
                ssr_url=one_ssr_url
            ))
            ssr_list.append(ssr_config)
        else:
            print("ssr_url[{}] parse error!".format(one_ssr_url))

    # get_avg_latency of each ssr
    result = []
    pool = multiprocessing.Pool(config['parallet'])
    for id, one_task in enumerate(ssr_list):
        port = one_task['local_port'] + id + 1
        one_task['local_port'] = port
        # result.append(pool.apply_async(get_latency_of_proxy, (json_ssr_conf, port)))
        pool.apply_async(get_latency_of_proxy, (one_task, '%d/%d' % (id, len(ssr_list))),
                         callback=lambda x: result.append(x))

    logging.info('Waiting for all subprocesses done...')
    pool.close()
    pool.join()

    # 保存结果
    config['ssr_config'].update({'{}:{}'.format(one['server'], one['server_port']): one for one in result})
    if config['mongo']:
        dump_ssr_to_mongo(config['ssr_config'].values())

    logging.info('The top 5:')
    result = sorted(result, key=lambda x: x['latency'])
    for one_result in result[:1]:
        pts = PrettyTable(one_result.keys())
        for one_result in result[:5]:
            pts.add_row(one_result.values())
        logging.info("\n{}".format(pts.get_string(fields=[
            "latency", "server", "server_port", "password", "method",
            "protocol", "protocol_param", "obfs", "obfs_param"
        ])))

    if result and result[0]['latency'] < 1:
        logging.info('update ssr config')
        update_ssr_config(result[0], config['target_config'])
    else:
        logging.info("not best ssr config for update")

    logging.info('all task done')
