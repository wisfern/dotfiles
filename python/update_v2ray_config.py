# -*- coding: utf-8 -*-
# Author: Wisfern
# Create Date: 2018-06-23
# for v2ray shashowsock_config.json
# history: 2018-12-05 update for v2ray 4.7

import json
from pymongo import MongoClient

config = {
    'target_config': 'v2ray_config.json',
    'mongo': {
        'host': '172.16.1.13',
        'port': 27017
    }
}


def load_ssr_from_mongo():
    mc = MongoClient(**config['mongo'])
    mc.server_info()
    ssr_db = mc['proxy']
    ssr_coll = ssr_db['ss_config']
    cursor = ssr_coll.find({'latency': {'$lt': 4}}, {'_id': 0, 'ssr_url': 0})
    if cursor:
        return list(cursor)
    else:
        return []


def load_vmess_from_mongo():
    mc = MongoClient(**config['mongo'])
    mc.server_info()
    ssr_db = mc['proxy']
    ssr_coll = ssr_db['vmess_config']
    cursor = ssr_coll.find({'latency': {'$lt': 4}}, {'_id': 0, 'vmess_url': 0})
    if cursor:
        return list(cursor)
    else:
        return []


def update_ssr_config(v2ray_config):
    """
    更新ss客户端正式配置文件
    :param v2ray_config:
    :type v2ray_config: dict
    :return: new v2ray_config
    """
    # 读取新的SS配置
    ssr_config = load_ssr_from_mongo()
    for one in ssr_config:
        one['group'] = 'xiezhifeng.cn'

    v2ray_ss_list = []
    for idx, one in enumerate(ssr_config):
        if one['method'] in ['rc4-md5', 'aes-128-ctr', 'rc4']:
            continue
        v2ray_ss_list.append({
            'email': '{}@test.com'.format(idx),
            'address': one['server'],
            'port': one['server_port'],
            'method': one['method'],
            'password': one['password'],
            'ota': False,
            'level': 0
        })

    new_r2vay_config = v2ray_config.copy()
    if v2ray_ss_list:
        for ss_config in new_r2vay_config['outbounds']:
            if ss_config['protocol'] == 'shadowsocks':
                ss_config['settings']['servers'] = v2ray_ss_list
                print("update {} ss config to v2ray".format(len(v2ray_ss_list)))
    else:
        print("未找到有效的ss代理，不更新配置")

    return new_r2vay_config


def update_vmess_config(v2ray_config):
    """
    更新vmess协议客户端正式配置文件
    :param v2ray_config:
    :type v2ray_config: dict
    :return: new v2ray_config
    """
    # 读取新的vmess配置
    vmess_config = load_vmess_from_mongo()

    v2ray_vmess_list = []
    # TODO: 添加变更逻辑
    # 先删除掉旧的vmess协议
    # 再追加新的vmess协议配置
    for idx, one in enumerate(vmess_config):
        v2ray_vmess_list.append({
            'email': '{}@test.com'.format(idx),
            'address': one['server'],
            'port': one['server_port'],
            'method': one['method'],
            'password': one['password'],
            'ota': False,
            'level': 0
        })

    new_r2vay_config = v2ray_config.copy()
    if v2ray_vmess_list:
        for ss_config in new_r2vay_config['outbounds']:
            if ss_config['protocol'] == 'shashowsocks':
                ss_config['settings']['servers'] = v2ray_vmess_list
                print("update {} vmess config to v2ray".format(idx+1))
    else:
        print("未找到有效的ss代理，不更新配置")

    return new_r2vay_config


def update_v2ray_config(ssr_config, to=None):
    """
    更新ssr客户端正式配置文件
    :param ssr_config:
    :type ssr_config: list
    :param to: ssr客户端文件路径
    :return:
    """
    if not to:
        to = "v2ray_config.json"

    with open(to, encoding='utf-8') as file:
        raw_v2ray_conf = json.loads(file.read())

    v2ray_config = update_ssr_config(raw_v2ray_conf)
    # v2ray_config = update_vmess_config(v2ray_config)

    with open(to, "w", encoding="utf-8") as fileto:
        json.dump(v2ray_config, fileto, indent=4)


if __name__ == '__main__':
    update_v2ray_config(config['target_config'])
