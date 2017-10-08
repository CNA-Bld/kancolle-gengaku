import json
import os

JSON_DB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/json-db/db/'

data = {}

classes = {}

with open(JSON_DB_PATH + 'ship_classes.nedb', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        this_class = json.loads(line)
        classes[this_class['id']] = this_class['name']['ja_jp']

with open(JSON_DB_PATH + 'ships.nedb', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        ship = json.loads(line)
        data[str(ship['id'])] = {'id': str(ship['id']), 'name': ship['name']['ja_jp'], 'ctype': classes.get(ship['class'], ''),
                                 'cid': ship['class_no'] or ''}
