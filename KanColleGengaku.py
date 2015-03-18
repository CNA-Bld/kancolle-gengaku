from store import *

from flask import Flask, render_template, request, after_this_request
import json
from io import BytesIO as IO
import gzip
import functools
from math import sqrt


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if response.status_code < 200 or response.status_code >= 300 or 'Content-Encoding' in response.headers:
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


app = Flask(__name__)

ship_types = {'19': '工作艦', '15': '補給艦', '12': '超弩級戦艦', '3': '軽巡洋艦', '5': '重巡洋艦', '18': '装甲空母', '6': '航空巡洋艦', '16': '水上機母艦', '13': '潜水艦', '17': '揚陸艦',
              '1': '海防艦', '2': '駆逐艦', '4': '重雷装巡洋艦', '9': '戦艦', '8': '高速戦艦', '14': '潜水空母', '7': '軽空母', '11': '正規空母', '10': '航空戦艦'}
ship_list = eval(redis.get('ship_list'))
ship_names = {}
for t in ship_list.values():
    for ship_id in t:
        ship_names[ship_id] = t[ship_id]
ship_list_sorted = [{'id': i, 'name': ship_types[i], 'ships': []} for i in sorted(ship_types.keys(), key=lambda x: int(x))]
for ship_type in ship_list_sorted:
    if ship_type['id'] in ship_list:
        ship_type['ships'] = [{'id': i, 'name': ship_list[ship_type['id']][i]} for i in sorted(ship_list[ship_type['id']], key=lambda x: int(x))]


@app.route('/')
@gzipped
def index():
    return render_template('index.html', ship_list=ship_list_sorted)


@app.route('/get')
@gzipped
def get_data():
    gengaku_table = eval(redis.get('gengaku_table'))
    target_ships = set(filter(lambda x: x, request.args.get('ships', '').split(',')))
    for ship in target_ships:
        if ship not in ship_names:
            return '蛤？You trying attack me meh?'
    results = {}
    for cons_type in ['general', 'large']:
        results[cons_type] = []
        for (key, value) in gengaku_table[cons_type].items():
            intersect = target_ships.intersection(set(value['results'].keys()))
            if intersect:
                succ_individual = {i: value['results'][i] for i in intersect}
                succ_sum = sum(succ_individual.values())
                probability = succ_sum / value['sum']
                results[cons_type].append({'resource': key, 'probability': probability,
                                           'succ_sum': succ_sum, 'succ_individual': succ_individual,
                                           'sum': value['sum'], 'stddev': sqrt(probability * (1 - probability) / value['sum'])})
        results[cons_type].sort(key=lambda x: x['probability'], reverse=True)
    return render_template('result.html', results=results, target_ships={i: ship_names[i] for i in target_ships}, list=list)


@app.route('/recipe')
@gzipped
def get_recipe():
    gengaku_table = eval(redis.get('gengaku_table'))
    cons_type = request.args.get('type', '')
    recipe = tuple(json.loads(request.args.get('recipe', '')))
    return render_template('recipe.html', recipe=recipe, result=gengaku_table[cons_type][recipe], ship_names=ship_names)


@app.route('/gengaku2/')
@gzipped
def gengaku2_index():
    return render_template('gengaku2.html', ship_list=ship_list_sorted)


@app.route('/gengaku2/get')
@gzipped
def gengaku2_get():
    gengaku2_table = eval(redis.get('gengaku2_table'))
    ship_id = request.args.get('id', '')
    if ship_id not in ship_names:
        return '蛤？You trying attack me meh?'
    return render_template('gengaku2_result.html', name=ship_names[ship_id], result=gengaku2_table[ship_id], cons_name={'general': '普建', 'large20': '大建 / 20 资材', 'large1': '大建 / 1 资材神教'}.get)


if __name__ == '__main__':
    app.run(debug=False)
