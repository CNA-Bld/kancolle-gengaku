import json
import requests
import re

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


def distance(recipe1, recipe2):
    return sum([(recipe1[i] - recipe2[i]) ** 2 for i in range(4)])


def build_gengaku2():
    temp_table = {}
    for c, d in gengaku_table.items():
        for recipe, result in d.items():
            for ship, number in result['results'].items():
                if ship not in temp_table:
                    temp_table[ship] = {i: {} for i in ['general', 'large20', 'large1']}
                if c == 'general':
                    temp_table[ship][c][recipe] = result['sum'] / number
                else:
                    if recipe[4] == 20:
                        temp_table[ship]['large20'][recipe] = result['sum'] / number
                    elif recipe[4] == 1:
                        temp_table[ship]['large1'][recipe] = result['sum'] / number
    result_table = {}
    for ship, data in temp_table.items():
        result_table[ship] = {}
        for c in ['general', 'large20', 'large1']:
            if data[c]:
                centers = [[0] * 4, [0] * 4]
                weights = [0, 0]
                tmp = 0
                for recipe, weight in data[c].items():
                    for i in range(4):
                        centers[tmp][i] += weight * recipe[i]
                    weights[tmp] += weight
                    tmp = 1 - tmp
                for i in range(2):
                    for j in range(4):
                        centers[i][j] /= weights[i]
                for round in range(10):
                    new_centers = [[0] * 4, [0] * 4]
                    weights = [0, 0]
                    for recipe, weight in data[c].items():
                        if distance(recipe, centers[0]) < distance(recipe, centers[1]):
                            for i in range(4):
                                new_centers[0][i] += weight * recipe[i]
                            weights[0] += weight
                        else:
                            for i in range(4):
                                new_centers[1][i] += weight * recipe[i]
                            weights[1] += weight
                    for i in range(2):
                        for j in range(4):
                            centers[i][j] = new_centers[i][j] / weights[i]
                result_table[ship][c] = centers
    redis.set('gengaku2_table', repr(result_table))


def main():
    ship_list = get_ship_list()
    for t in ship_list.values():
        for ship_id in t:
            # ship_names[ship_id] = t[ship_id]
            process_construct_data(get_construct_data(ship_id))
    redis.set("ship_list", repr(ship_list))
    redis.set("gengaku_table", repr(gengaku_table))
    build_gengaku2()


if __name__ == '__main__':
    main()
