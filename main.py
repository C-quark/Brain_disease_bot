import telebot
import random
import sqlite3
from config import token

bot = telebot.TeleBot(token)

@bot.message_handler(commands = ['start'])
def send_start(message):
   buttoms_markup = telebot.types.ReplyKeyboardMarkup(True)
   buttoms_markup.row('/start', '/help', '/get_disease')
   result = bot.send_message(message.from_user.id, 'Сколько тебе лет?', reply_markup = buttoms_markup)
   bot.register_next_step_handler(result, handle_age)

@bot.message_handler(commands = ['get_disease'])
def get_disease(message):
    result = bot.send_message(message.from_user.id, 'Напиши болезнь, дурында')
    bot.register_next_step_handler(result, handle_disease)

@bot.message_handler(commands = ['help'])
def send_help(message):
    bot.send_message(message.from_user.id, 'Ты думаешь, что я тебе помогать стану?')

d_commands = {'/start' : send_start, '/get_disease': get_disease}

def handle_disease(message):
    if message.text in d_commands:
        d_commands[message.text](message)
    else:
        disease = message.text
        with sqlite3.connect('brain') as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.execute('select description from disease_name as n, disease_description as d where (n.description_id = d.id and lower(name) = lower (\'' + disease + '\'))')
            result = db_cursor.fetchall()
            result2 = bot.reply_to(message, result)
            bot.register_next_step_handler(result2, handle_disease)

def handle_age(message):
    if message.text.isdigit():
        age = int(message.text)
        if age < 18:
            bot.reply_to(message, 'Малявка')
        elif age < 30:
            bot.reply_to(message, 'Ты в самом соку, если ты не Валера')
        elif age < 50:
            result = bot.reply_to(message, 'Какие цветы на могилку ты предпочитаешь?')
            bot.register_next_step_handler(result, flower)
        else:
            result = bot.reply_to(message, 'Давно разлагаешься?')
            bot.register_next_step_handler(result, yes_no)
            return
    else:
        result = bot.reply_to(message, 'Пиши возраст!')
        bot.register_next_step_handler(result, handle_age)
        return

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    greetings = ['Привет', 'Добрый день', 'Добрый вечер', 'Доброй ночи', 'Здравствуй', 'Доброе утро']
    answers = ['Привет', 'Доброго времени суток', 'Здравствуй']
    if message.text in greetings:
        bot.reply_to(message, random.choice(answers))
    elif message.text in d_commands:
        d_commands[message.text](message)
    else:
        bot.reply_to(message, 'Не пиши херню')

def flower(message):
    if message.text in d_commands:
        d_commands[message.text](message)
    else:
        answer = message.text.lower()
        bot.reply_to(message, 'Ты реально думаешь, что я принесу тебе ' + answer)

def yes_no(message):
    if message.text in d_commands:
        d_commands[message.text](message)
    else:
        answer = message.text.lower()
        if answer == 'Да':
            bot.reply_to(message, 'Да ты динозавр!')
        elif answer == 'Нет':
            bot.reply_to(message, 'Даже не успел собой покормить червей, тормоз')
        else:
            bot.reply_to(message, 'Удачного разложения')

bot.polling(none_stop = True, interval = 0)
