from flask import Flask, request
from flask_restful import Resource, Api
import urllib.request
import json
from ieee_xplore_extract import XPLORE
from json import dumps
from flask import jsonify
import urllib.parse

app = Flask(__name__)


@app.route('/data_api/query=<search_query>')
def get(search_query):
    temp_query = search_query
    params = {'q': search_query}
    search_query = urllib.parse.urlencode(params)
    search_query = search_query[2:len(search_query)]
    file_name = 'http://api.springernature.com/metadata/json?q=keyword:' + search_query + '&api_key=...'
    file_name_elsevier = 'https://api.elsevier.com/content/search/scopus?query=' + search_query + '&apiKey=...'

    # Search by year: http://api.springernature.com/meta/v2/jats?q=year:2007&api_key=
    # Search by subject: http://api.springernature.com/openaccess/jats?q=subject:Chemistry&api_key=
    # Search by isbn : http://api.springernature.com/metadata/json?q=isbn:978-0-387-79148-7&api_key=

    query = XPLORE('...')
    query.abstractText(temp_query)
    query.dataFormat('json')

    # ieee_data
    data_ieee = query.callAPI()
    data_ieee = json.loads(data_ieee)

    json_url = urllib.request.urlopen(file_name)
    json_url_elsevier = urllib.request.urlopen(file_name_elsevier)

    # springer_data
    data_springer = json.loads(json_url.read())

    # elsevier_data
    data_elsevier = json.loads(json_url_elsevier.read())

    data_dict = {}
    data_dict.__setitem__('Title', [])
    data_dict.update({'DOI': []})
    data_dict.update({'Author_Name': []})
    data_dict.update({'Publication_Name': []})
    data_dict.update({'Publication_Date': []})
    data_dict.update({'Link': []})

    for els in data_elsevier['search-results']['entry']:
        try:
            data_dict['Title'].append(els['dc:title'])
        except KeyError:
            data_dict['Title'].append('-')

        try:
            data_dict['DOI'].append(els['prism:doi'])
        except KeyError:
            data_dict['DOI'].append('-')

        try:
            data_dict['Publication_Name'].append(els['prism:publicationName'])
        except KeyError:
            data_dict['Publication_Name'].append('-')

        try:
            data_dict['Publication_Date'].append(els['prism:coverDate'])
        except KeyError:
            data_dict['Publication_Date'].append('-')

        try:
            data_dict['Title'].append(els['dc:title'])
        except KeyError:
            data_dict['Title'].append('-')

        data_dict['Author_Name'].append(els['dc:creator'])

        try:
            data_dict['Link'].append(els['link'][2]['@href'])
        except KeyError:
            data_dict['Link'].append('-')

    for spr in data_springer['records']:
        data_dict['Title'].append(spr['title'])
        data_dict['DOI'].append(spr['doi'])
        data_dict['Publication_Name'].append(spr['publicationName'])
        data_dict['Publication_Date'].append(spr['publicationDate'])
        temp = []
        for j in spr['creators']:
            temp.append(j['creator'])
        data_dict['Author_Name'].append(temp)
        data_dict['Link'].append(spr['url'][0]['value'])

    for ie in data_ieee['articles']:
        data_dict['Title'].append(ie['title'])
        try:
            data_dict['DOI'].append(ie['doi'])
        except KeyError:
            data_dict['DOI'].append('-')

        try:
            data_dict['Publication_Name'].append(ie['publication_title'])
        except KeyError:
            data_dict['Publication_Name'].append('-')
        try:
            data_dict['Publication_Date'].append(ie['publication_date'])
        except KeyError:
            data_dict['Publication_Date'].append('-')

        temp = []
        for itr in ie['authors']['authors']:
            temp.append(itr['full_name'])
        data_dict['Author_Name'].append(temp)
        try:
            data_dict['Link'].append(ie['html_url'])
        except KeyError:
            data_dict['Link'].append('-')

    return jsonify(data_dict)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
