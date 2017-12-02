from flask import Flask, jsonify
from flask import request
import requests
import api_manager
import xmltodict as xdict

API_KEY = 'Rtg1zFQ4gVGVAb3bO0LBw'
API_SECRET = 'POW5s9DW2I8pxz5pO5q5ymeUzmsqp6aakVASmgPy4M'


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/')
def hello_world():
    return 'Python API for UHAC.'


@app.route('/books', methods=['GET'])
def get_books():
    name = request.args.get('title')
    url_goodreads = 'https://www.goodreads.com/book/title.xml'
    url_ibooks = 'http://itunes.apple.com/lookup'
    data_goodreads = {
        'title': name,
        'key': API_KEY
    }
    req_goodreads = api_manager.get_request(url_goodreads, data=data_goodreads)
    encoded = req_goodreads.text.encode("utf8")
    resp_goodreads = xdict.parse(encoded)

    title = resp_goodreads['GoodreadsResponse']['book']['title']
    isbn13 = resp_goodreads['GoodreadsResponse']['book']['isbn13']
    author = resp_goodreads['GoodreadsResponse']['book']['authors']['author']
    data_ibooks = {'isbn': isbn13}
    print data_ibooks
    print req_goodreads.url
    req_ibooks = api_manager.get_request(url_ibooks, data=data_ibooks)
    resp_ibooks = req_ibooks.json()
    print resp_ibooks
    price = resp_ibooks['results'][0]['formattedPrice']
    buy_link = resp_ibooks['results'][0]['trackViewUrl']
    return jsonify({
        'title': title,
        'author': author,
        'price': price,
        'buy_link': buy_link,
    })


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0', threaded=True)
