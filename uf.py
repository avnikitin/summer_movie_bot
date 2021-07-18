# transliterates from russian to english
symbols = (
u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ",
(*list(u'abvgde'), 'yo', 'zh', *list(u'zijklmnoprstuf'), 'kh', 'z', 'ch', 'sh',
 'sh', '',
 'y', '\'', 'e', 'yu', 'ya', *list(u'ABVGDE'), 'Yo', 'ZH',
 *list(u'ZIJKLMNOPRSTUF'), 'Kh', 'Z', 'Ch', 'Sh', 'Sh', *list(u'_Y_E'), 'Yu',
 'Ya', ' '))

coding_dict = {source: dest for source, dest in zip(*symbols)}


def transliterate(text):
    res = ""
    for c in text:
        if c in coding_dict.keys():  # a russian letter
            res += coding_dict[c]
        else:  # an english letter or a special symbol
            res += c
    return res


# calculates edit distance between strings a and b in O(|a| * |b|) time and space
def calc_levenstein(a, b):
    a = a.lower()
    b = b.lower()
    # add fictive element to get 1-indexation
    a = '#' + a
    b = '#' + b

    n = len(a)
    m = len(b)

    # D[i][j] stores levenstein distance for strings a[1..i] and b[1..j]
    D = [[0 for y in range(m)] for x in range(n)]
    D[0][0] = 0

    for i in range(1, n):
        D[i][0] = i
    for j in range(1, m):
        D[0][j] = j

    for i in range(1, n):
        for j in range(1, m):
            D[i][j] = max(n, m)
            # make prefices of length i-1 and j-1 equal and then change last symbol if necessary
            D[i][j] = min(D[i][j], D[i - 1][j - 1] + (a[i] != b[j]))

            # erase last symbol of one of the strings
            D[i][j] = min(D[i][j], min(D[i][j - 1] + 1, D[i - 1][j] + 1))
    return D[n - 1][m - 1]


# calculates date of the next wednesday or thursday
import datetime
from datetime import date


def weekday(day):
    # variable day is either 'wed' or 'thu' 
    num = 0
    if day == 'wed':
        num = 2
    else:
        num = 3
    today = date.today()
    days_ahead = (num - today.weekday()) % 7
    return today + datetime.timedelta(days_ahead)


def get_url(data):
    day = ''
    if (data.day < 10):
        day = '0' + str(data.day)
    else:
        day = str(data.day)
    month = ''
    if (data.month < 10):
        month = '0' + str(data.month)
    else:
        month = str(data.month)
    return f"https://kinomax.ru/izhevsk#{data.year}-{month}-{day}"


import requests
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict


def get_list_of_movies(link):
    Headers = CaseInsensitiveDict()
    Headers[
        'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    Headers[
        'Cookie'] = "PHPSESSID=9ujmk8efsr0qipsg7iub2lvajs; _fbp=fb.1.1626515665173.793115199; _ga=GA1.2.941780321.1626515666; _gid=GA1.2.1958022850.1626515666; _ym_d=1626515666; _ym_isad=2; _ym_uid=1626515666356562953; _ym_visorc=w; city=21; directCrm-session=%7B%22deviceGuid%22%3A%2261f0ebb8-b06c-4349-b84b-71aaf1bcabe5%22%7D; last_visit=1626501992594::1626516392594; mindboxDeviceUUID=61f0ebb8-b06c-4349-b84b-71aaf1bcabe5; top100_id=t1.6116028.1314559964.1626515666208"
    response = requests.get(link, headers=Headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    movies = []
    hrefs = soup.select('a[href]')
    for href in hrefs:
        if (href.get('href')[0:9] == '/filmdata'):
            movies.append(href.get_text())
    return movies


def get_name_prediction(name):
    url = f'https://www.imdb.com/find?q={name}&s=nm&ref_=fn_al_nm_mr'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    hrefs = soup.select('a[href]')
    prescribed_name = ''
    link = 'https://www.imdb.com'
    nm_link = ''
    for href in hrefs:
        if (href.get('href')[0:5] == '/name' and href.get_text() != ''):
            prescribed_name = href.get_text()
            added = href.get('href')
            link += added
            nm_link = added[6:len(added) - 1]
            break
    return [prescribed_name, nm_link, link]


import config
import random


def get_link_to_a_random_movie(nm_link):
    url = "https://imdb8.p.rapidapi.com/actors/get-all-filmography"

    print(nm_link)
    querystring = {"nconst": nm_link}

    headers = {
        'x-rapidapi-key': config.X_RAPIDAPI_KEY,
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    ind = response.text.find("filmography")
    if (response.text[ind + 13] == 'n'):
        return 'no movies found'
    Dict = eval(response.text)
    films = Dict['filmography']

    title_links = []
    for film in films:
        title_links.append(film['id'])

    if (len(title_links) == 0):
        return 'no movies found'

    rand_title_link = title_links[random.randint(0, len(title_links) - 1)]
    return 'imdb.com' + rand_title_link
