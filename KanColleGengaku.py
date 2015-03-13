from store import *

from flask import Flask, render_template

app = Flask(__name__)


ship_types = {'19': '工作艦', '15': '補給艦', '12': '超弩級戦艦', '3': '軽巡洋艦', '5': '重巡洋艦', '18': '装甲空母', '6': '航空巡洋艦', '16': '水上機母艦', '13': '潜水艦', '17': '揚陸艦', '1': '海防艦', '2': '駆逐艦', '4': '重雷装巡洋艦', '9': '戦艦', '8': '高速戦艦', '14': '潜水空母', '7': '軽空母', '11': '正規空母', '10': '航空戦艦'}
ship_list = eval(redis.get('ship_list'))

@app.route('/')
def index():
    ship_list_sorted = [{'id': i, 'name': ship_types[i], 'ships': []} for i in sorted(ship_types.keys(), key=lambda x: int(x))]
    for ship_type in ship_list_sorted:
        if ship_type['id'] in ship_list:
            ship_type['ships'] = [{'id': i, 'name': ship_list[ship_type['id']][i]} for i in sorted(ship_list[ship_type['id']], key=lambda x: int(x))]
    #print(ship_list_sorted)
    return render_template('index.html', ship_list=ship_list_sorted)


if __name__ == '__main__':
    app.run(debug=True)
