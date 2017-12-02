# -*- coding: utf-8 -*-

import helpers
import constants
import requests
import api_manager
import image_search

from flask import Flask, jsonify
from flask import request

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])


@app.route('/pronto-py/api')
def hello_world():
    return 'Python API for UHAC.'


@app.route('/pronto-py/api/search', methods=['POST'])
def get_info():
    image = request.files['file']
    if image.filename is None:
        image_url = ''
    else:
        image_url = helpers.upload(image)

    code = image_search.do_image_search(image_url)
    results = image_search.parse_results(code)

    return results

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
