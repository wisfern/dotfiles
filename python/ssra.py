# -*- coding: utf-8 -*-
# Author: Wisfern
# Create Date: 2018-06-15
# 运行方法，在root用户下，并cd到ssr安装目录，同级目录有一个config.json文件
# pip3 install requests[socks]
# python3 ssa.py
import base64
import json
import multiprocessing
import re
import logging
import subprocess
import time
from pprint import pprint
from urllib import parse, request

import requests
logging.basicConfig(level=logging.INFO)

config = {
    'sub_urls': [
        'https://yzzz.ml/freessr/',
    ],
    'url_list': [
        'ssr://MTY1LjIyNy42Mi4xODI6MTkwMjA6b3JpZ2luOnJjNC1tZDU6cGxhaW46Y0dGemN6a3dNakEvP29iZnNwYXJhbT0mcmVtYXJrcz02WUM0NVllaA',
    ],
    'test_latency_urls': [
        # "https://www.google.com",
        # "https://twitter.com",
        "https://api.lbank.info",
        "https://data.gate.io/api2/1/public"
    ],
    # 'ssr_bin': 'shadowsocks/shadowsocks-local.exe'
    'ssr_bin': 'shadowsocks/local.py',
    'target_config': 'config.json',
    'parallet': 30,
    'proxies': {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
}


def get_latency(url):
    logging.info("test the latency of " + url + "...")
    start = time.time()
    try:
        r = request.urlopen(url, timeout=5)
    except Exception as e:
        logging.error("this socks proxy may be invalid, %s", e)
        return 6   # 已经是无效的ssr了
    end = time.time()
    # logging.debug( r.read() )
    latency = end - start
    logging.info("the latency of " + url + " is " + str(latency))
    return latency


def get_average_latency():
    urls = config['test_latency_urls']
    latencysum = 0
    for url in urls:
        latencysum += get_latency(url)
    averagelatency = latencysum / len(urls)
    logging.info("the average latency is " + str(averagelatency))
    return averagelatency


# 延迟测试进程
def get_latency_of_proxy(ssr_config, port=1080):
    """
    针对一个ssr代理配置开一条进程测试代理延迟
    :param ssr_config: json配置
    :type ssr_config: str
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

    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", port)
    socket.socket = socks.socksocket
    socket.create_connection = create_connection

    config_filename = '.'.join(['_'.join(["config", str(port)]), "json"])
    logging.debug("Testing " + ssr_config + "...")
    try:
        # 设置config.json文件
        f = open("shadowsocks/%s" % config_filename, "w")
        f.write(ssr_config)
        f.close()
        # 启动shadowsocks代理程序
        # cmd = ["shadowsocks/shadowsocks-local.exe","-c","shadowsocks/config.json"]
        cmd = [config['ssr_bin'], "-c", "shadowsocks/%s" % config_filename]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        a = get_average_latency()
        p.kill()
        time.sleep(0.5)
        return (a, ssr_config)
    except Exception as e:
        logging.error("get_latency_of_proxy error = %s" % e)
        return (10, ssr_config)


def parseSub(sub_url):
    logging.info("get sub url text...")
    data = requests.get(sub_url, proxies=config['proxies'])
    if data and data.status_code == 200:
        return str(base64.standard_b64decode(data.text), encoding="utf-8")
        # return base64.urlsafe_b64decode(data.text)


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
        sb64obfsparam = url_param_dict.get("obfsparam", "")
        sb64protoparam = url_param_dict.get("protoparam", "")
        sb64remarks = url_param_dict.get("remarks", "")
        sb64group = url_param_dict.get("group", "")

        ssr_url_dict = dict(
            server=sserver,
            server_port=int(sserver_port),
            password=b64decode(spassword),
            method=smethod,
            protocol=sprotocol,
            protocol_param=b64decode(sb64protoparam),
            obfs=sobfs,
            obfs_param=b64decode(sb64obfsparam)
        )
        return ssr_url_dict
    else:
        return dict()


def b64decode(b64str):
    """自动补全结尾的=号"""
    missing_padding = 4 - len(b64str) % 4
    if missing_padding:
        b64str += '=' * missing_padding
    return str(base64.urlsafe_b64decode(b64str), encoding="utf-8")


def update_ssr_config(ssr_config_json, to=None):
    if not to:
        to = "config.json"

    with open(to) as file:
        raw_ssr_conf = json.loads(file.read())

    ssr_config = json.loads(ssr_config_json)
    ssr_config['local_port'] = 1080
    raw_ssr_conf.update(ssr_config)
    with open(to, "w") as fileto:
        json.dump(raw_ssr_conf, fileto, indent=4)


if __name__ == "__main__":
    ssr_list = []                           # 保存ssr解析后的配置
    ssr_url_list = config['url_list']       # 保存ssr://协议
    for one_ssr_sub in config['sub_urls']:
        data = parseSub(one_ssr_sub)
        ssr_url_list = list(set(data.split('\r\n')) | set(ssr_url_list))

    logging.info("get {} ssr url from suburl[{}]".format(len(ssr_url_list), config['sub_urls']))
    for one_ssr_url in ssr_url_list:
        ssr_config = parse_b64ssr_to_dict(one_ssr_url)
        if ssr_config:
            ssr_config.update(dict(local_port=1080, timeout=600))
            # jsonstring = json.dumps(ssr_config)
            # print(jsonstring)
            # ssr_list.append(jsonstring)
            ssr_list.append(ssr_config)
        else:
            print("ssr_url parse error!")

    # get_avg_latency of each ssr
    pool = multiprocessing.Pool(config['parallet'])
    result = []
    for id, one_task in enumerate(ssr_list):
        port = one_task['local_port'] + id + 1
        one_task['local_port'] = port
        json_ssr_conf = json.dumps(one_task)
        # result.append(pool.apply_async(get_latency_of_proxy, (json_ssr_conf, port)))
        pool.apply_async(get_latency_of_proxy, (json_ssr_conf, port), callback=lambda x: result.append(x))

    logging.info('Waiting for all subprocesses done...')
    pool.close()
    pool.join()

    logging.info('The top 5:')
    result = sorted(result, key=lambda x: x[0])
    for one_result in result[:5]:
        logging.info(one_result)
    # pprint(result)
    # latency_list = []
    # for one_result in result:
    #     latency_list.append(one_result.get(0))
    #
    # latency_list = sorted(latency_list, key=lambda x: x[0])
    # for one_latency in latency_list:
    #     logging.info(one_latency)

    logging.info('update ssr config')
    update_ssr_config(result[0][1], config['target_config'])

    logging.info('all task done')
