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
    file_name = 'http://api.springernature.com/metadata/json?q=keyword:' + search_query + '&api_key=7014ed4b31d43e56e2743c3752d0c4c9'
    file_name_elsevier = 'https://api.elsevier.com/content/search/scopus?query=' + search_query + '&apiKey=a58bb91bfad077e15dbd4fd7835ed3ba'

    # Search by year: http://api.springernature.com/meta/v2/jats?q=year:2007&api_key=
    # Search by subject: http://api.springernature.com/openaccess/jats?q=subject:Chemistry&api_key=
    # Search by isbn : http://api.springernature.com/metadata/json?q=isbn:978-0-387-79148-7&api_key=

    query = XPLORE('jn52p9296a56tcm2j3tn2768')
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
    data_dict.__setitem__('_Articles', [])


    # ELSEVIER
    for els in data_elsevier['search-results']['entry']:
        sub_dict = {}
        sub_dict.__setitem__('Title', '')
        sub_dict.update({'DOI': ''})
        sub_dict.update({'Author_Name': []})
        sub_dict.update({'Publication_Name': ''})
        sub_dict.update({'Publication_Date': ''})
        sub_dict.update({'Link': ''})
        try:
            sub_dict['Title'] = (els['dc:title'])
        except KeyError:
            sub_dict['Title'] = '-'

        try:
            sub_dict['DOI'] = (els['prism:doi'])
        except KeyError:
            sub_dict['DOI'] = '-'

        try:
            sub_dict['Publication_Name'] = (els['prism:publicationName'])
        except KeyError:
            sub_dict['Publication_Name'] = '-'

        try:
            sub_dict['Publication_Date'] = (els['prism:coverDate'])
        except KeyError:
            sub_dict['Publication_Date'] = '-'

        try:
            sub_dict['Title'] = (els['dc:title'])
        except KeyError:
            sub_dict['Title'] = '-'

        sub_dict['Author_Name'] = (els['dc:creator'])

        try:
            sub_dict['Link'] = (els['link'][2]['@href'])
        except KeyError:
            sub_dict['Link'] = '-'
        data_dict['_Articles'].append(sub_dict)


    # SPRINGER
    for spr in data_springer['records']:
        sub_dict = {}
        sub_dict.__setitem__('Title', '')
        sub_dict.update({'DOI': ''})
        sub_dict.update({'Author_Name': []})
        sub_dict.update({'Publication_Name': ''})
        sub_dict.update({'Publication_Date': ''})
        sub_dict.update({'Link': ''})
        try:
            sub_dict['Title'] = (spr['title'])
        except KeyError:
            sub_dict['Title'] = '-'

        try:
            sub_dict['DOI'] = (spr['doi'])
        except KeyError:
            sub_dict['DOI'] = '-'
        try:
            sub_dict['Publication_Name'] = (spr['publicationName'])
        except:
            sub_dict['Publication_Name'] = '-'

        try:
            sub_dict['Publication_Date'] = (spr['publicationDate'])
        except KeyError:
            sub_dict['Publication_Date'] = '-'
        for j in spr['creators']:
            sub_dict['Author_Name'].append(j['creator'])

        sub_dict['Link'] = (spr['url'][0]['value'])
        data_dict['_Articles'].append(sub_dict)


    # IEEE
    for ie in data_ieee['articles']:
        sub_dict = {}
        sub_dict.__setitem__('Title', '')
        sub_dict.update({'DOI': ''})
        sub_dict.update({'Author_Name': []})
        sub_dict.update({'Publication_Name': ''})
        sub_dict.update({'Publication_Date': ''})
        sub_dict.update({'Link': ''})
        sub_dict['Title'] = (ie['title'])
        try:
            sub_dict['DOI'] = (ie['doi'])
        except KeyError:
            sub_dict['DOI'] = '-'

        try:
            sub_dict['Publication_Name'] = (ie['publication_title'])
        except KeyError:
            sub_dict['Publication_Name'] = '-'
        try:
            sub_dict['Publication_Date'] = (ie['publication_date'])
        except KeyError:
            sub_dict['Publication_Date'] = '-'

        temp = []
        for itr in ie['authors']['authors']:
            sub_dict['Author_Name'].append(itr['full_name'])

        try:
            sub_dict['Link'] = (ie['html_url'])
        except KeyError:
            sub_dict['Link'] = '-'

        data_dict['_Articles'].append(sub_dict)

    return jsonify(data_dict)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
