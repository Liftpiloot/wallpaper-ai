import datetime
import openai
import os
from dotenv import load_dotenv
import pathlib
import geocoder
from openai import OpenAI
import requests
import ctypes
import urllib.request
import time


def get_weather(lon, lat, openweather_api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={openweather_api_key}"
    owm_response = requests.get(url)
    owm_response_json = owm_response.json()
    return owm_response_json


def create_prompt(location, weather):
    client = OpenAI()
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"image generation prompt for a painting of {location} with this weather: {weather}",
        max_tokens=300,
    )
    return response.choices[0].text


def generate_image(prompt):
    client = OpenAI()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url


def save_image(image_url, filename):
    # Send a GET request to the image URL
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open a new file in binary write mode
        with open(filename, 'wb') as file:
            # Write the content of the response to the file
            file.write(response.content)


def set_wallpaper(filename):
    file = os.path.abspath(filename)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, file, 0)


def run_program():

    # Load .env file
    path = pathlib.Path(__file__).parent / 'api_key.env'
    # Set openAI api key from .env file
    load_dotenv(path)
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Get OpenWeather API key from .env file
    load_dotenv(path)
    openweather_api_key = os.getenv('OPENWEATHER_API_KEY')

    # get location from ip address
    g = geocoder.ip('me')
    lat, lon = g.latlng

    # Get weather data from OpenWeather API
    weather = get_weather(lon, lat, openweather_api_key)
    location = f"{weather['name']} located in {weather['sys']['country']}"

    # Create prompt for OpenAI
    prompt = create_prompt(location, weather)

    # Generate image from prompt
    image_url = generate_image(prompt)

    # save image file
    filename = f"wallpaperAI_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    save_image(image_url, filename)

    # Set image as wallpaper
    set_wallpaper(filename)


def wait_for_internet_connection():
    while True:
        try:
            response = urllib.request.urlopen('https://www.google.com', timeout=1)
            return
        except urllib.request.URLError:
            pass
        time.sleep(1)


wait_for_internet_connection()
run_program()
