#!/usr/bin/env python
from config import TOKEN
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, PicklePersistence
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import json
import locale

# set russian locale
locale.setlocale(locale.LC_ALL, "ru_RU.utf8")

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    """ asks for city and provider, prints out start menu """
    
    # if city/provider is not set, ask for it
    if not context.user_data.get('city'):
        change_city(update, context)
        return
    if not context.user_data.get('provider'):
        change_provider(update, context)
        return

    keyboard = [[InlineKeyboardButton("Прогноз на сегодня", callback_data='today'),
                 InlineKeyboardButton("Прогноз на завтра", callback_data="tomorrow"),
                 InlineKeyboardButton("Прогноз на неделю", callback_data="week")],
                [InlineKeyboardButton("Настройки", callback_data="settings"),
                 InlineKeyboardButton("Список команд", callback_data="help")],]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "Главное меню."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

def display_help(update, context):
    text = """
/start - вывести главное меню
/city - поменять город
/provider - поменять сайт для прогнозов
/help - вывести это сообщение
/today - вывести прогноз на сегодня
/tomorrow - вывести прогноз на завтра
/week - вывести прогноз на неделю
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    """ takes a list of buttons and makes a keyboard markup with n columns out of it """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

def change_city(update, context):
    """ asks user to choose a city for forecasts """
    text = "Выберите город для которого вы хотите получать прогнозы погоды:"
    keyboard = []
    for city in context.bot_data['cities']:
        keyboard.append(InlineKeyboardButton(city.capitalize(), callback_data=city))

    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

def change_provider(update, context):
    """ asks user what site does he want to use as a provider for forecasts """
    text = "Выберите сайт с которого вы хотите получать прогнозы:"
    keyboard = []
    for provider in context.bot_data['providers']:
        keyboard.append(InlineKeyboardButton(provider.capitalize(), callback_data=provider))

    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

def print_daily_forecast(update, context, day='today'):
    """ prints forecast for today or tomorrow """
    city = context.user_data['city']
    provider =  context.user_data['provider']
    data = context.bot_data['forecast_data']
    for d in data: 
        if d['city'] == city and d['provider'] == provider:
                forecast = d['forecast'][day]

    message = f"Прогноз погоды на {'сегодня' if day == 'today' else 'завтра'} ({(datetime.date.today() if day == 'today' else datetime.date.today() + datetime.timedelta(days=1)).strftime('%A, %e %B')}):\n"

    for f in forecast:
        if f['time'] in ["9:00", "15:00", "21:00"]:
            message += f"""
*{f['time']}* {f['temperature']} {f['description']} {f['emoji']}
{'Осадки: ' + f['precipitation'] + ' мм' if provider == 'gismeteo' else 'Вероятность осадков: ' + f['precipitation_chance'] + '%'}
Ветер: {f['windspeed'] + ' м/c'}
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='markdown')

def print_weekly_forecast(update, context):
    """ prints forecast for a week """
    city = context.user_data['city']
    provider =  context.user_data['provider']
    data = context.bot_data['forecast_data']

    for d in data:
        if d['city'] == city and d['provider'] == provider:
            forecast = d['forecast']['week']

    message = f"Прогноз погоды на неделю ({datetime.date.today().strftime('%A, %e %B')} - {(datetime.date.today() + datetime.timedelta(days=6)).strftime('%A, %e %B')}):\n"

    for f in forecast:
        date = datetime.datetime.strptime(f['date'], '%Y-%m-%d')
        message += f"""
*{datetime.datetime.strftime(date,'%A')}*:
Мин.: {f['min_temp']}. Макс.: {f['max_temp']} 
{f['description']} {f['emoji']}
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='markdown')

def change_settings(update, context):
    """ sends a menu for changing settings """
    text = "Настройки"
    keyboard = [
        [
            InlineKeyboardButton("Изменить город", callback_data="city"),
            InlineKeyboardButton("Изменить сайт прогнозов", callback_data="provider"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

def query_handler(update, context):
    query = update.callback_query
    if query.data == "today" or query.data == "tomorrow":
        print_daily_forecast(update, context, query.data)
        start(update, context)
    elif query.data == "week":
        print_weekly_forecast(update, context)
        start(update, context)
    elif query.data == "settings":
        change_settings(update, context)
    elif query.data == "city":
        change_city(update, context)
    elif query.data == "provider":
        change_provider(update, context)
    elif query.data == 'menu':
        start(update, context)
    elif query.data == 'help':
        display_help(update, context)
        start(update, context)
    elif query.data in context.bot_data['cities']:
        context.user_data['city'] = query.data
        query.answer("Город успешно изменен!")
        start(update, context)
    elif query.data in context.bot_data['providers']:
        context.user_data['provider'] = query.data
        query.answer("Сайт успешно изменен!")
        start(update, context)

    query.message.delete()
    query.answer()

def print_tomorrow_forecast(update, context):
    print_daily_forecast(update, context, 'tomorrow')

def main():
    persistence_file = PicklePersistence(filename='data/bot_persistence')
    updater = Updater(token=TOKEN, use_context=True, persistence=persistence_file)

    # add command handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('city', change_city))
    updater.dispatcher.add_handler(CommandHandler('provider', change_provider))
    updater.dispatcher.add_handler(CommandHandler('today', print_daily_forecast))
    updater.dispatcher.add_handler(CommandHandler('tomorrow', print_tomorrow_forecast))
    updater.dispatcher.add_handler(CommandHandler('week', print_weekly_forecast))
    updater.dispatcher.add_handler(CommandHandler('help', display_help))
    updater.dispatcher.add_handler(CallbackQueryHandler(query_handler))

    # load data
    with open("data/weather_data.json", "r") as f:
        updater.dispatcher.bot_data['forecast_data'] = json.loads(f.read())
    with open("data/city_data.json", "r") as f:
        data = json.loads(f.read())
    updater.dispatcher.bot_data['cities'] = set(d['city'] for d in data)
    updater.dispatcher.bot_data['providers'] = set(d['provider'] for d in data)
    
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
