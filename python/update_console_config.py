# -*- coding: utf-8 -*-
# Author: Wisfern
# Create Date: 2018-06-23
# for windows gui-config.json
import json
import logging

from pymongo import MongoClient, ASCENDING

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s %(message)s', level=logging.INFO)

config = {
    'target_config': 'config.json',
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
    cursor = ssr_coll.find({}, {'_id': 0}).sort([('latency', ASCENDING)])
    if cursor:
        return list(cursor)
    else:
        return []


def update_ssr_config(ssr_config, to=None):
    """
    更新ssr客户端正式配置文件
    :param ssr_config:
    :type ssr_config: list
    :param to: ssr客户端文件路径
    :return:
    """
    if not to:
        to = "config.json"

    with open(to, encoding='utf-8') as file:
        raw_ssr_conf = json.loads(file.read())

    # ssr_config = json.loads(ssr_config_json)
    del ssr_config['ssr_url']
    raw_ssr_conf.update(ssr_config)
    with open(to, "w", encoding="utf-8") as fileto:
        json.dump(raw_ssr_conf, fileto, indent=4)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: {} <server:ip>".format(sys.argv[0]))
        sys.exit(-1)

    server, ip = sys.argv[1].split(':', 1)
    ssr_config = load_ssr_from_mongo()
    search_result = list(filter(lambda x: x['server'] == server and x['server_port'] == int(ip), ssr_config))
    if search_result:
        # 转换为config的格式
        logging.info('update ssr config.json success => {}:{}\n{}'.format(server, ip, search_result[0]['ssr_url']))
        update_ssr_config(search_result[0], config['target_config'])
    else:
        logging.info('can\'n find {}:{} ssr config'.format(server, ip))
