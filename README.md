# Weatherbot
Weatherbot is a simple telegram bot for displaying weather forecasts in Ukraine.  

## Demo
![Demo](demo.gif)

[Link to the bot](https://t.me/ukraine_weather_bot)

# Installation
## Clone the repo
From github:

    git clone https://github.com/ArthurBais/weatherbot 
    # alternative link: git://git.arthurbais.xyz/weatherbot
    
    
## Install the required python modules:

    pip install -r requirements.txt
    
## Configure crontab

The program consists of two scripts: `weatherbot.py` and `weather_forecast.py`.  
`weather_forecast.py` is used to scrape the forecasts from gismeteo.ua and 
synoptik.ua for cities in `data/city_data.json` and store the data in
`data/weather_data.json`.  

For the data to be up to date, `weather_forecast.py` needs to be run daily,
for example as a cronjob:

    crontab -e
    
    00 00 * * * /path/to/script/weather_forecast.py # execute script every day at 00:00

# Running the bot
`weatherbot.py` is the actual bot that serves users with forecasts
from `data/weather_data.json`  
Launch it with `python weatherbot.py`
