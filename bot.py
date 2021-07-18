import telebot
import config
from telebot import types
import requests
from bs4 import BeautifulSoup
from PIL import Image
import urllib.request

# UF stands for useful functions
from uf import transliterate
from uf import calc_levenstein
from uf import weekday
from uf import get_url
from uf import get_list_of_movies
from uf import get_name_prediction
from uf import get_link_to_a_random_movie

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    hi_pic = open('hi_pic.webp', 'rb')
    bot.send_sticker(message.chat.id, hi_pic)
    bot.send_message(message.chat.id,
                     ('Привет!\n Этот бот умеет делать 2 вещи:\n' +
                      '1) По имени и фамилии актера, режиссера или ' +
                      'любого другого причастного к киноискусству человека' +
                      ' выдавать его фото и случайный фильм, снятый при' +
                      'участии этого человека и \n 2) показывать премьеры' +
                      'в кинотеатре "Киномакс" на этой неделе'))


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, (
                'Просто введите имя и фамилию (по-русски или по-английски), ' +
                'а мы постараемся отыскать такого человека и покажем его фото,' +
                'если найдем такое'))


@bot.message_handler(commands=['movie_premieres'])
def find_premieres(message):
    respond = ''
    old_movies = get_list_of_movies(get_url(weekday('wed')))
    new_movies = get_list_of_movies(get_url(weekday('thu')))
    premieres = []
    for movie in new_movies:
        if not movie in old_movies:
            premieres.append(movie)
    respond = ''
    if (len(premieres) == 0):
        respond = 'К сожалению, в этот четверг никаких новых фильмов :('
    else:
        respond = 'Вот список премьер в этот четверг:\n'
        for movie in premieres:
            respond += movie + '\n'
        respond += 'Купить билет можно по ссылке' + get_url(weekday('thu'))
    bot.send_message(message.chat.id, respond)


@bot.message_handler(content_types=['text'])
def handle(message):
    if (message.text == 'премьеры в кино'):
        find_premieres(message)
    else:
        name = message.text
        name = transliterate(name)
        name = name.replace(' ', '%20')
        predicted_name, nm_link, link = get_name_prediction(name)
        if (predicted_name == ''):
            respond = 'Нам не удалось найти никого с таким или похожим именем :('
            bot.send_message(message.chat.id, respond)
            return
        respond = ''
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        imgs = soup.find_all('div', 'image')
        if (calc_levenstein(name, predicted_name) >= 4):
            respond += 'Вы допустили достаточно много ошибок, поэтому мы не можем ручаться, что показываем вам того, кого вы хотите\n'
        if (len(imgs) == 0):
            respond += 'Мы нашли человека с именем ' + predicted_name + ', но, к сожалению, ни одной его фотографии :('
            bot.send_message(message.chat.id, respond)
        else:
            srces = imgs[0].find_all('img')
            if (len(srces) == 0):
                respond += 'Мы нашли человека с именем ' + predicted_name + ', но, к сожалению, ни одной его фотографии :('
                bot.send_message(message.chat.id, respond)
            else:
                url = imgs[0].img['src']
                respond += 'Вот фото человека по имени ' + predicted_name
                bot.send_message(message.chat.id, respond)
                im = Image.open(requests.get(url, stream=True).raw)
                bot.send_photo(message.chat.id, im)

        link_to_a_movie = get_link_to_a_random_movie(nm_link)
        print(link_to_a_movie)
        if (link_to_a_movie == 'no movies found'):
            bot.send_message(message.chat.id,
                             'К сожалению, мы не нашли ни одного фильма с участием этого человека :(')
        else:
            bot.send_message(message.chat.id,
                             'Вот случайный фильм, снятый при участии этого человека:' + link_to_a_movie)


bot.polling(none_stop=True)
