# -*- coding: utf-8 -*-

import math
import json
import helpers
import constants
import requests
import api_manager

from flask import Flask, jsonify
from flask import request

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])


@app.route('/pronto-py/api')
def hello_world():
    return 'Python API for UHAC.'


@app.route('/pronto-py/api/search', methods=['GET'])
def get_info():
    search = request.args.get('food')
    results = dict()
    food = constants.food_101[search]

    # Call edamam for food parser
    food_uri = get_food(food)

    # Call edamam for nutrients
    nutrients = get_nutrients(food_uri)
    nutrients['name'] = food
    return jsonify(nutrients)


def get_food(food):
    data = {
        'ingr': food,
        'app_id': constants.EDAMAM_APP_ID,
        'app_key': constants.EDAMAM_APP_KEY,
        'page': 0,
    }
    req = api_manager.get_request(constants.EDAMAM_FOOD_API, data=data)
    result = req.json()
    return result['parsed'][0]['food']['uri']


def get_nutrients(food_uri):
    food_data = {
        'yield': 1,
        'ingredients': [
            {
                'quantity': 1,
                'measureURI': 'http://www.edamam.com/ontologies/edamam.owl#Measure_unit',
                'foodURI': food_uri
            }
        ]
    }
    url = constants.EDAMAM_NUTRIENTS_API.format(
        app_id=constants.EDAMAM_APP_ID,
        app_key=constants.EDAMAM_APP_KEY,
    )
    req = api_manager.post_request(url, data=food_data)
    result = req.json()

    data = dict()
    data['calories'] = result['calories']

    nutrients = []
    for item in result['totalNutrients']:
        nutri = dict()
        nutri['label'] = result['totalNutrients'][item]['label']
        nutri['unit'] = result['totalNutrients'][item]['unit']
        nutri['quantity'] = math.ceil(result['totalNutrients'][item]['quantity'] * 100) / 100.0
        nutrients.append(nutri)
    data['nutrients'] = nutrients
    return data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
