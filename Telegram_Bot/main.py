import telebot
import requests
import datetime
import pytz
import random
from telebot import types
from geopy.geocoders import Nominatim

# Токен вашего бота
TOKEN = '7036019304:AAEkmicbRDHbOA0hgDEzeQ7XcnfEOCCgWvk'

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Замените 'YOUR_API_KEY' на ваш API ключ с OpenWeatherMap
API_KEY = '233619f6b20bc7ebabafa99053bb28f6'

# Словарь для хранения выбранных пользователем городов
user_cities = {}

# Словарь для отслеживания состояний пользователей
user_states = {}

# Добавим геокодер для определения местоположения по координатам
geolocator = Nominatim(user_agent="telegram-weather-bot")

weather_translation = {
    "Thunderstorm": "Гроза",
    "Drizzle": "Морось",
    "Rain": "Дождь",
    "Snow": "Снег",
    "Mist": "Туман",
    "Smoke": "Дым",
    "Haze": "Мгла",
    "Dust": "Пыль",
    "Fog": "Туман",
    "Sand": "Песок",
    "Ash": "Пепел",
    "Squall": "Шквал",
    "Tornado": "Торнадо",
    "Clear sky": "Ясно",
    "Clouds": "Облачно",
    "Few clouds": "Небольшая облачность",
    "Scattered clouds": "Переменная облачность",
    "Broken clouds": "Облачно с прояснениями",
    "Overcast clouds": "Пасмурно",
    "Sunny": "Солнечно",
    "Partly сloudy": "Переменная облачность",
    "Mostly сloudy": "В основном облачно",
    "Light rain": "Легкий дождь",
    "Heavy rain": "Сильный дождь",
    "Showers": "Ливень",
    "Light snow": "Легкий снег",
    "Heavy snow": "Сильный снег",
    "Blizzard": "Метель",
    "Ice cellets": "Ледяные кристаллы",
    "Freezing rain": "Ледяной дождь"
}

weather_emojis = {
    "Гроза": "⛈️",
    "Морось": "🌧️",
    "Дождь": "🌧️",
    "Снег": "❄️",
    "Туман": "🌫️",
    "Дым": "🌫️",
    "Мгла": "🌫️",
    "Пыль": "🌫️",
    "Песок": "🌫️",
    "Пепел": "🌫️",
    "Шквал": "🌬️",
    "Торнадо": "🌪️",
    "Ясно": "☀️",
    "Облачно": "☁️",
    "Небольшая облачность": "🌤️",
    "Переменная облачность": "🌥️",
    "Облачно с прояснениями": "🌥️",
    "Пасмурно": "☁️",
    "Солнечно": "☀️",
    "В основном облачно": "🌥️",
    "Легкий дождь": "🌧️",
    "Сильный дождь": "🌧️",
    "Ливень": "⛈️",
    "Легкий снег": "🌨️",
    "Сильный снег": "🌨️",
    "Метель": "❄️❄️❄️",
    "Ледяные кристаллы": "🌨️",
    "Ледяной дождь": "🌨️☔"
}

# Функция для получения прогноза погоды
def get_weather(city, days):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "cnt": days * 8  # Количество прогнозов на каждый день
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

# Функция для получения температуры за конкретное время суток
def get_temperature_by_time(data, target_time, forecast_index):
    for forecast in data["list"][forecast_index:forecast_index+8]:  # Учитываем прогнозы только для текущего дня
        forecast_time = datetime.datetime.fromtimestamp(forecast["dt"], tz=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        if forecast_time.strftime('%H:%M') == target_time:
            return round(forecast["main"]["temp"])
    return None

import random

def recommend_clothing(temperature, weather_description, humidity, wind_speed):
    recommendations = {
        "Cold": [["теплый свитер", "пуховик", "шапка", "теплые кеды", "перчатки"],
                 ["теплая кофта", "куртка", "шапка", "шарф", "джинсы"],
                 ["зимняя обувь", "свитшот", "теплые джинсы", "меховая шапка", "куртка"]],
        "Mild": [["свитер", "легкая куртка", "туфли", "джинсы", "футболка"],
                 ["кепка", "джинсовка", "кроссовки", "джинсы", "рубашка"],
                 ["кеды", "спортивные штаны", "толстовка", "куртка", "футболка"]],
        "Warm": [["кепка", "футболка", "шорты", "кеды", "сандалии"],
                 ["спортивка", "футблока", "сланцы", "шорты", "футболка"],
                 ["легкая юбка", "платье", "босоножки", "футболка", "шорты"]],
        "Hot": [["футболка", "бриджи", "шлепанцы", "шорты", "легкий топ"],
                ["панама", "шорты", "майка", "очки", "сандалии"],
                ["кроссовки", "футболка", "спортивки", "кепка", "шорты"],
                ["легкое платье", "балетки", "панама", "шорты", "очки"]],
        "Snowy": [["зимняя куртка", "шапка с ушами", "теплые ботинки", "варежки", "шарф"],
                  ["пуховик", "шапка", "шарф", "перчатки", "теплые ботинки"],
                  ["зимний плащ", "шапка", "теплая обувь", "перчатки", "шарф"]],
        "Rainy": [["зонтик", "дождевик", "кеды", "спортивные штаны", "толстовка", "куртка"],
                  ["плащ", "дождевик", "джинсовка", "резиновые сапоги", "шапка", "шарф"],
                  ["водонепроницаемая куртка", "резиновые сапоги", "шапка", "теплые джинсы", "зонтик"]],
        "Windy": [["ветровка", "шарф", "шапка", "джинсы", "туфли"],
                  ["ветровка", "плащ", "шарф", "куртка", "брюки"],
                  ["ветровка", "шапка", "теплая кофта", "шарф", "перчатки"]],
        "Very Cold": [["теплая куртка", "шапка", "теплые ботинки", "подштанники", "варежки"],
                      ["шапка", "пальто", "шарф", "варежки", "угги"],
                      ["шапка", "теплая обувь", "термобелье", "перчатки", "пуховик"],
                      ["пуховик", "подштанники", "шарф", "утепленные штаны", "зимние ботинки"]],
        "Unknown": [["Обычная одежда"]]
    }

    # Определение категории погоды
    if temperature < -5:
        category = "Very Cold"
    elif temperature < 5:
        category = "Cold"
    elif temperature < 15:
        category = "Mild"
    elif temperature < 25:
        category = "Warm"
    else:
        category = "Hot"

    return random.choice(recommendations.get(category, [["Обычная одежда"]]))

# Функция для создания кнопок
def create_buttons():
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton('Выбрать город'),
               types.KeyboardButton('Отправить геолокацию'),
               types.KeyboardButton('Погода на сегодня'),
               types.KeyboardButton('Погода на 3 дня'),
               types.KeyboardButton('Погода на 5 дней'))
    return markup

# Переменная для отслеживания выбора города
city_set = False

# Функция для проверки существования города
def check_city_existence(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
    response = requests.get(url)
    data = response.json()
    if data:
        return True
    else:
        return False

def reset_state(user_id):
    if user_id in user_states:
        del user_states[user_id]

# Функция для обработки отправленной геолокации
@bot.message_handler(content_types=['location'])
def handle_location(message):
    global city_set
    latitude = message.location.latitude
    longitude = message.location.longitude
    location = geolocator.reverse(f"{latitude}, {longitude}")
    city = location.raw.get('address', {}).get('city')
    if city:
        user_cities[message.chat.id] = city
        bot.send_message(message.chat.id, f"Установлен город {city}. Теперь вы можете узнать прогноз погоды.")
        city_set = True
    else:
        bot.send_message(message.chat.id, "Не удалось определить город по вашей геолокации.")

    # Добавим код для обновления меню после отправки геолокации
    markup = create_buttons()

# Функция для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global city_set
    markup = create_buttons()
    bot.reply_to(message, "Привет! Я телеграм бот Smart Weather. Выберите команду из меню чтобы начать.", reply_markup=markup)

# Функция для установки города
def set_city(message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_city"  # Устанавливаем состояние "waiting_city" для пользователя
    bot.reply_to(message, "Введите название вашего города:")

# Функция для проверки существования города
def check_city_existence(city, country=None):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json"}
    if country:
        params["countrycodes"] = country
    response = requests.get(base_url, params=params)
    data = response.json()
    if data:
        return True
    else:
        return False


# Функция для обработки введенного пользователем города
def process_city_step(message):
    user_id = message.from_user.id
    city = message.text
    country = None  # Добавляем возможность указания страны
    if check_city_existence(city, country):
        user_cities[user_id] = city  # Сохраняем выбранный город
        user_states[user_id] = None  # Сбрасываем состояние пользователя
        bot.reply_to(message, f"Установлен город {city}. Теперь вы можете узнать прогноз погоды.")
    else:
        bot.reply_to(message, "Город не найден. Пожалуйста, введите корректное название города.")


# Функция для получения прогноза погоды для указанного пользователем города
def get_weather_for_user_city(user_id, days):
    if user_id not in user_cities:
        return None
    city = user_cities[user_id]
    try:
        return get_weather(city, days)
    except Exception as e:
        return None

def today(message):
    global city_set
    user_id = message.from_user.id
    city_name = user_cities.get(user_id, "Неизвестный город")
    data = get_weather_for_user_city(user_id, 1)

    # Для каждого времени суток получаем температуру
    temperatures = {}
    for time in ["06:00", "12:00", "18:00", "00:00"]:
        temperature = get_temperature_by_time(data, time, 0)  # Используем индекс 0 для первого дня
        temperatures[time] = temperature

    weather_info = data["list"][0]
    weather_time = datetime.datetime.fromtimestamp(weather_info["dt"], tz=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
    date = weather_time.strftime('%d-%m-%Y')
    weather_description_en = weather_info["weather"][0]["description"].capitalize()
    weather_description_ru = weather_translation.get(weather_description_en, weather_description_en)
    weather_emoji = weather_emojis.get(weather_description_ru, "")
    wind_speed = weather_info["wind"]["speed"]
    humidity = weather_info["main"]["humidity"]
    pressure = weather_info["main"]["pressure"]
    recommendation = recommend_clothing(temperatures["12:00"], weather_description_ru, humidity, wind_speed)

    bot.reply_to(message, f"Город: {city_name}\n"
                          f"📅 Текущая дата: {date}\n"
                          f"{weather_description_ru} {weather_emoji}\n"
                          f"🌕 Утро: {temperatures.get('06:00', 'Нет данных')}°C\n"
                          f"🌖 День: {temperatures.get('12:00', 'Нет данных')}°C\n"
                          f"🌘 Вечер: {temperatures.get('18:00', 'Нет данных')}°C\n"
                          f"🌑 Ночь: {temperatures.get('00:00', 'Нет данных')}°C\n"
                          f"Скорость ветра: {wind_speed} м/с\n"
                          f"Влажность: {humidity}%\n"
                          f"Давление: {pressure} мм рт. ст.\n"
                          f"Рекомендации по выбору одежды: {', '.join(recommendation)}")

# Функция для команды /threedays
@bot.message_handler(commands=['threedays'])
def threedays(message):
    global city_set
    user_id = message.from_user.id
    city_name = user_cities.get(user_id, "Неизвестный город")
    data = get_weather_for_user_city(user_id, 3)

    weather_forecast = ""
    for i in range(3):
        forecast_index = i * 8  # Учитываем индекс каждого дня в списке прогнозов
        if forecast_index < len(data["list"]):
            weather_info = data["list"][forecast_index]
            weather_time = datetime.datetime.fromtimestamp(weather_info["dt"], tz=pytz.utc).astimezone(
                pytz.timezone('Europe/Moscow'))
            date = weather_time.strftime('%d-%m-%Y')

            # Задаем время для получения температуры
            target_times = ["06:00", "12:00", "18:00", "00:00"]  # утро, день, вечер, ночь
            temperatures = {}
            for time in target_times:
                temperature = get_temperature_by_time(data, time, forecast_index)
                if temperature is not None:
                    temperatures[time] = temperature

            weather_description_en = weather_info["weather"][0]["description"].capitalize()
            weather_description_ru = weather_translation.get(weather_description_en, weather_description_en)
            weather_emoji = weather_emojis.get(weather_description_ru, "")
            wind_speed = weather_info["wind"]["speed"]
            humidity = weather_info["main"]["humidity"]
            pressure = weather_info["main"]["pressure"]

            forecast_for_day = (f"📅 {date} \n"
                                f"{weather_description_ru} {weather_emoji}\n"
                                f"🌕 Утро: {temperatures.get('06:00', 'Нет данных')}°C\n"
                                f"🌖 День: {temperatures.get('12:00', 'Нет данных')}°C\n"
                                f"🌘 Вечер: {temperatures.get('18:00', 'Нет данных')}°C\n"
                                f"🌑 Ночь: {temperatures.get('00:00', 'Нет данных')}°C\n"
                                f"Скорость ветра: {wind_speed} м/с\n"
                                f"Влажность: {humidity}%\n"
                                f"Давление: {pressure} мм рт. ст.\n\n")
            weather_forecast += forecast_for_day

    bot.reply_to(message, f"Погода в городе {city_name} на 3 дня:\n\n{weather_forecast}")

# Функция для команды /fivedays
@bot.message_handler(commands=['fivedays'])
def fivedays(message):
    global city_set
    user_id = message.from_user.id
    city_name = user_cities.get(user_id, "Неизвестный город")
    data = get_weather_for_user_city(user_id, 5)

    weather_forecast = ""
    for i in range(5):
        forecast_index = i * 8  # Учитываем индекс каждого дня в списке прогнозов
        if forecast_index < len(data["list"]):
            weather_info = data["list"][forecast_index]
            weather_time = datetime.datetime.fromtimestamp(weather_info["dt"], tz=pytz.utc).astimezone(
                pytz.timezone('Europe/Moscow'))
            date = weather_time.strftime('%d-%m-%Y')

            # Задаем время для получения температуры
            target_times = ["06:00", "12:00", "18:00", "00:00"]  # утро, день, вечер, ночь
            temperatures = {}
            for time in target_times:
                temperature = get_temperature_by_time(data, time, forecast_index)
                if temperature is not None:
                    temperatures[time] = temperature

            weather_description_en = weather_info["weather"][0]["description"].capitalize()
            weather_description_ru = weather_translation.get(weather_description_en, weather_description_en)
            weather_emoji = weather_emojis.get(weather_description_ru, "")
            wind_speed = weather_info["wind"]["speed"]
            humidity = weather_info["main"]["humidity"]
            pressure = weather_info["main"]["pressure"]

            forecast_for_day = (f"📅 {date} \n"
                                f"{weather_description_ru} {weather_emoji}\n"
                                f"🌕 Утро: {temperatures.get('06:00', 'Нет данных')}°C\n"
                                f"🌖 День: {temperatures.get('12:00', 'Нет данных')}°C\n"
                                f"🌘 Вечер: {temperatures.get('18:00', 'Нет данных')}°C\n"
                                f"🌑 Ночь: {temperatures.get('00:00', 'Нет данных')}°C\n"
                                f"Скорость ветра: {wind_speed} м/с\n"
                                f"Влажность: {humidity}%\n"
                                f"Давление: {pressure} мм рт. ст.\n\n")
            weather_forecast += forecast_for_day

    bot.reply_to(message, f"Погода в городе {city_name} на 5 дней:\n\n{weather_forecast}")

# Функция для обработки нажатий кнопок и ввода города
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    if message.text == 'Выбрать город':
        set_city(message)
    elif message.text == 'Погода на сегодня':
        reset_state(user_id)  # Сбрасываем состояние ожидания города
        if user_id not in user_cities or user_cities[user_id] is None:
            bot.reply_to(message, "Пожалуйста, установите город с помощью команды 'Выбрать город' или 'Отправить геолокацию'.")
        else:
            today(message)
    elif message.text == 'Погода на 3 дня':
        reset_state(user_id)  # Сбрасываем состояние ожидания города
        if user_id not in user_cities or user_cities[user_id] is None:
            bot.reply_to(message, "Пожалуйста, установите город с помощью команды 'Выбрать город' или 'Отправить геолокацию'.")
        else:
            threedays(message)
    elif message.text == 'Погода на 5 дней':
        reset_state(user_id)  # Сбрасываем состояние ожидания города
        if user_id not in user_cities or user_cities[user_id] is None:
            bot.reply_to(message, "Пожалуйста, установите город с помощью команды 'Выбрать город' или 'Отправить геолокацию'.")
        else:
            fivedays(message)
    elif message.text == 'Отправить геолокацию':
        reset_state(user_id)  # Сбрасываем состояние ожидания города
        request_location(message)
    elif user_id in user_states and user_states[user_id] == "waiting_city":
        process_city_step(message)  # Обрабатываем введенный город
    else:
        bot.reply_to(message, "Используйте команды из меню для взаимодействия с ботом.")

# Функция для запроса геолокации
def request_location(message):
    markup = create_buttons()  # Используем функцию для создания кнопок
    bot.send_message(message.chat.id, "Пожалуйста, отправьте ваше местоположение.", reply_markup=markup)

# Запускаем бота
bot.polling()

