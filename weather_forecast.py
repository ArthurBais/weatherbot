#!/usr/bin/env python
from bs4 import BeautifulSoup, NavigableString
from config import HEADERS
import requests
import datetime
import json
import re

def gismeteo_fetch(data):
    """ scrapes weather forecast from gismeteo.ua """

    gismeteo_data = []

    cities = set(d['city'] for d in data) # set contains only unique elements(city names here)
    for city in cities:

        # get url from dictionary
        url = next(d['url'] for d in data if d['city'] == city and d['provider'] == 'gismeteo')

        response = requests.get(url + "/today", timeout=5, headers=HEADERS).text
        soup = BeautifulSoup(response, "lxml")
        widget = soup.find('div', class_="widget__container")
        temperatures = widget.find_all('span', class_="unit unit_temperature_c")
        descriptions = widget.find_all('span', class_="tooltip")
        windspeeds = widget.find_all('span', class_="unit unit_wind_m_s")
        precipitations = widget.find_all('div', class_="w_prec__value")

        # today's weather report
        today = []
        time = 0
        for i in range(len(windspeeds)):
            today.append({
                "time": f"{time}:00",
                "temperature": temperatures[i].text,
                "description": descriptions[i]['data-text'],
                "windspeed": windspeeds[i].text.strip(),
                "precipitation": precipitations[i].text.strip() if precipitations else '0',
                'emoji': emojify(descriptions[i]['data-text'])
            })
            time += 3

        response = requests.get(url+ "/tomorrow", timeout=5, headers=HEADERS).text
        soup = BeautifulSoup(response, "lxml")
        widget = soup.find('div', class_="widget__container")
        temperatures = widget.find_all('span', class_="unit unit_temperature_c")
        descriptions = widget.find_all('span', class_="tooltip")
        windspeeds = widget.find_all('span', class_="unit unit_wind_m_s")
        precipitations = widget.find_all('div', class_="w_prec__value")

        # tomorrows weather report
        tomorrow = []
        time = 0
        for i in range(len(windspeeds)):
            tomorrow.append({
                "time": f"{time}:00",
                "temperature": temperatures[i].text,
                "description": descriptions[i]['data-text'],
                "windspeed": windspeeds[i].text.strip(),
                "precipitation": precipitations[i].text.strip() if precipitations else '0',
                'emoji': emojify(descriptions[i]['data-text'])
            })
            time += 3

        response = requests.get(url + "/10-days", timeout=5, headers=HEADERS).text
        soup = BeautifulSoup(response, "lxml")
        widget = soup.find('div', class_="widget__container")
        descriptions = widget.find_all('span', class_="tooltip")
        windspeeds = widget.find_all('span', class_="unit unit_wind_m_s")
        precipitations = widget.find_all('div', class_="w_prec__value")
        max_ts = widget.find_all("div", class_='maxt')
        min_ts = widget.find_all("div", class_="mint")
        min_temperatures = []
        max_temperatures = []
        for i in range(len(max_ts)):
            max_temperatures.append(max_ts[i].find('span', class_='unit unit_temperature_c').text)
            min_temperatures.append(min_ts[i].find('span', class_='unit unit_temperature_c').text)

        # weekly weather report
        week = []

        for i in range(7):
            week.append({
                'date': f"{datetime.date.today() + datetime.timedelta(days=i)}",
                'max_temp': max_temperatures[i],
                'min_temp': min_temperatures[i],
                'description': descriptions[i]['data-text'],
                'windspeed': windspeeds[i].text.strip(),
                'precipitation': precipitations[i].text.strip(),
                'emoji': emojify(descriptions[i]['data-text'])
            })

        gismeteo_data.append({
            'provider': 'gismeteo',
            'city': city,
            'url': url,
            'forecast': {
                'today': today,
                'tomorrow': tomorrow,
                'week': week
            }
        })
    return gismeteo_data


def sinoptik_fetch(data):
    """ scrapes forecast data from sinoptik.ua """

    cities = set(d['city'] for d in data) # set contains only unique elements(city names here)

    sinoptik_data = []

    for city in cities:
        url = next(d['url'] for d in data if d['city'] == city and d['provider'] == 'sinoptik')
        # url = next(d['url'] for d in data if d['city'] == city and d['provider'] == 'sinoptik')

        response = requests.get(url + f'/{str(datetime.date.today())}', timeout=5, headers=HEADERS).text
        soup = BeautifulSoup(response,'lxml')
        main_content = soup.find('div', 'tabsContentInner')
        temps = main_content.find('tr', class_='temperature').find_all('td')
        descriptions = main_content.find_all('div', class_=re.compile('^weatherIco.*$'))
        windspeeds = main_content.find_all('div', class_=re.compile("^Tooltip wind.*$"))
        precip_chance = []
        for s in main_content.find_all('tr')[-1]:
            if isinstance(s, NavigableString):
                continue
            precip_chance.append(s.text if s.text != '-' else '0')
        today = []
        time = 0
        for i in range(len(temps)):
            today.append({
                'time': f"{time}:00",
                'temperature': temps[i].text,
                'description': descriptions[i]['title'],
                'windspeed': windspeeds[i].text,
                'precipitation_chance': precip_chance[i],
                'emoji': emojify(descriptions[i]['title'])
            })
            time += 3

        response = requests.get(url + f'/{str(datetime.date.today() + datetime.timedelta(days=1))}', timeout=5, headers=HEADERS).text
        soup = BeautifulSoup(response,'lxml')
        main_content = soup.find('div', 'tabsContentInner')
        temps = main_content.find('tr', class_='temperature').find_all('td')
        descriptions = main_content.find_all('div', class_=re.compile('^weatherIco.*$'))
        windspeeds = main_content.find_all('div', class_=re.compile("^Tooltip wind.*$"))
        precip_chance = []
        for s in main_content.find_all('tr')[-1]:
            if isinstance(s, NavigableString):
                continue
            precip_chance.append(s.text if s.text != '-' else '0')
        tomorrow = []
        time = 0
        for i in range(len(temps)):
            tomorrow.append({
                'time': f"{time}:00",
                'temperature': temps[i].text,
                'description': descriptions[i]['title'],
                'windspeed': windspeeds[i].text,
                'precipitation_chance': precip_chance[i],
                'emoji': emojify(descriptions[i]['title'])
            })
            time += 3


        soup = BeautifulSoup(response,'lxml')
        main_content = soup.find('div', 'tabs')
        max_temps = main_content.find_all('div', class_='max')
        min_temps = main_content.find_all('div', class_='min')
        descriptions = main_content.find_all('div', class_=re.compile('^weatherIco.*$'))
        week = []

        for i in range(7):
            week.append({
                'date': f"{datetime.date.today() + datetime.timedelta(days=i)}",
                'min_temp': max_temps[i].find('span').text,
                'max_temp': max_temps[i].find('span').text,
                'description': descriptions[i]['title'],
                'emoji': emojify(descriptions[i]['title'])
            })

        sinoptik_data.append({
            'provider': 'sinoptik',
            'city': city,
            'url': url,
            'forecast': {
                'today': today,
                'tomorrow': tomorrow,
                'week': week
            }
            })
    return sinoptik_data


def emojify(s):
    """ returns emojis based on forecast descriptions """
    if "ясно" in s.lower():
        return "☀️"
    elif "дождь" in s.lower() and "гроз" in s.lower():
        return "⛈"
    elif "дождь" not in s.lower() and "гроз" in s.lower():
        return "🌩"
    elif ("пасмурно" in s.lower() or "сплошная облачность" in s.lower()) and "дождь" in s.lower():
        return "🌧"
    elif "облач" in s.lower() and "дождь" in s.lower():
        return "🌦"
    elif "малооблачно" in s.lower() or "небольшая облачность" in s.lower():
        return "🌤"
    elif "пасмурно" in s.lower() or "сплошная облачность" in s.lower():
        return "☁️"
    elif "облач" in s.lower():
        return "🌥"
    return ""

def fetch_and_write():
    """ fetches data from all providers and saves it to a json file """
    with open("data/city_data.json", "r") as f:
        data = json.loads(f.read())
        gismeteo = gismeteo_fetch(data)
        sinoptik = sinoptik_fetch(data)

    with open("data/weather_data.json", "w", encoding="utf-8") as f:
        json.dump(gismeteo + sinoptik, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_and_write()

