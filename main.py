# -*- coding: utf-8 -*-

import math
import json
import constants
import requests
import requests_cache

from flask import Flask, jsonify
from flask import request

requests_cache.install_cache(cache_name='pronto_cache', backend='sqlite', expire_after=600000)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/py/pronto-py/api')
def hello_world():
    return 'Python API for UHAC.'


@app.route('/py/pronto-py/api/search', methods=['GET'])
def get_info():
    search = request.args.get('food')

    food = search.replace('_', ' ').title()

    # Call edamam for food_urid parser
    food_uri = get_food(food)

    # Call edamam for nutrients
    data = get_nutrients(food_uri)

    # Call zomato to get resto
    resto_data = get_restos(food)

    data['name'] = food
    data['restaurants'] = resto_data['restaurants']
    data['reviews'] = resto_data['reviews']
    return jsonify(data)


def get_food(food):
    params = {
        'ingr': food,
        'app_id': constants.EDAMAM_APP_ID,
        'app_key': constants.EDAMAM_APP_KEY,
        'page': 0,
    }
    req = requests.get(constants.EDAMAM_FOOD_API, params=params)
    result = req.json()
    return result['parsed'][0]['food']['uri']


@app.route('/py/pronto-py/api/checkout', methods=['POST'])
def checkout():
    content = request.get_json()
    merchant_id = content['merchant_id']
    product_id = content['product_id']
    quantity = content['quantity']

    params = {
        'merchant_id': merchant_id,
        'product_id': product_id,
        'quantity': quantity,
    }
    req = requests.post(constants.PRONTO_CHECKOUT_API, json=params)
    result = req.json()
    return result


def get_nutrients(food_uri):
    params = {
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
    req = requests.post(url, json=params)
    result = req.json()

    data = {}
    data['calories'] = result['calories']

    nutrients = []
    for item in result['totalNutrients']:
        nutri = {}
        nutri['label'] = result['totalNutrients'][item]['label']
        nutri['unit'] = result['totalNutrients'][item]['unit']
        nutri['quantity'] = math.ceil(result['totalNutrients'][item]['quantity'] * 100) / 100.0
        nutrients.append(nutri)
    data['nutrients'] = nutrients
    return data


def get_restos(food):
    params = {
        'q': food,
        'lat': 14.551418,
        'lon': 120.9871303,
        'count': 10,
        'radius': 2000,
    }
    headers = {
        "user-key": constants.ZOMATO_API_KEY,
        "Accept": 'application/json'
    }
    req = requests.get(constants.ZOMATO_SEARCH_API, params=params, headers=headers)
    result = req.json()
    resto_data = []

    for item in result['restaurants']:
        resto = {}
        resto['name'] = item['restaurant']['name']
        resto['id'] = item['restaurant']['id']
        resto['address'] = item['restaurant']['location']['address']
        resto['url'] = item['restaurant']['url']
        resto['image'] = item['restaurant']['thumb']
        rating = item['restaurant']['user_rating']['aggregate_rating']
        resto['rating'] = round(float(rating), 0) if rating != '0' else 4
        resto['is_pronto_merchant'] = False
        resto['products'] = []
        resto_data.append(resto)

    reviews = get_reviews(result['restaurants'][3]['restaurant']['id'])
    merchants = get_merchant_resto()
    for index, merchant in enumerate(merchants):
        for index, resto in enumerate(resto_data):
            if merchant['id'] == resto['id']:
                merchant['products'] = merchant['products']['data']
                resto_data[index] = merchant
                break
    data = {
        'restaurants': resto_data,
        'reviews': reviews
    }
    return data


def get_reviews(resto_id):
    params = {
        'res_id': resto_id
    }
    headers = {
        "user-key": constants.ZOMATO_API_KEY,
        "Accept": 'application/json'
    }
    req = requests.get(constants.ZOMATO_REVIEW_API, params=params, headers=headers)
    result = req.json()
    data = []
    for item in result['user_reviews']:
        review = {}
        review['rating'] = item['review']['rating']
        review['title'] = item['review']['rating_text']
        review['body'] = item['review']['review_text']
        data.append(review)
    return data


def get_merchant_resto():
    req = requests.get(constants.PRONTO_MERCHANT_API)
    result = req.json()
    return result['data']


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
