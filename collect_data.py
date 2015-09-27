import json
import requests
import re
from math import sqrt

from store import redis

HOME_URL = 'http://unlockacgweb.galstars.net/Kancollewiki/viewCreateShipLogList'
INFO_URL = 'http://unlockacgweb.galstars.net/Kancollewiki/viewCreateShipLog?sid='

gengaku_table = {'general': {}, 'large': {}}
ship_names = {}


def get_key(data_line):
    return tuple(data_line[i] for i in ["item" + str(i) for i in range(1, 6)])


def get_ship_list():
    content = requests.get(HOME_URL).text
    data = json.loads(re.search('var create_infos = (.+);', content).group(1))
    return data["ship_list"]


def get_construct_data(ship_id):
    content = requests.get(INFO_URL + str(ship_id)).text
    general_data = json.loads(re.search('var general_construction = (.+);', content).group(1))
    large_data = json.loads(re.search('var large_construction = (.+);', content).group(1))
    return {'general': general_data, 'large': large_data, 'ship': ship_id}


def process_construct_data(construct_data):
    print('Processing %s' % construct_data['ship'])
    for construct_type in ['general', 'large']:
        if construct_data[construct_type]:
            for order_by in ['order_by_succeed', 'order_by_probability']:
                for data_line in construct_data[construct_type][order_by]:
                    key = get_key(data_line)
                    if key not in gengaku_table[construct_type]:
                        gengaku_table[construct_type][key] = {'sum': int(data_line['sum']), 'results': {}}
                    gengaku_table[construct_type][key]['sum'] = max(int(data_line['sum']), gengaku_table[construct_type][key]['sum'])
                    gengaku_table[construct_type][key]['results'][construct_data['ship']] = int(data_line['succeed'])


def main():
    ship_list = get_ship_list()
    for t in ship_list.values():
        for ship_id in t:
            # ship_names[ship_id] = t[ship_id]
            process_construct_data(get_construct_data(ship_id))
    redis.set("ship_list", repr(ship_list))
    redis.set("gengaku_table", repr(gengaku_table))


if __name__ == '__main__':
    main()
