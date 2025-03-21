from tkinter import *
import locale
import threading
import time
import requests
import json
import traceback
import feedparser
from contextlib import contextmanager


from PIL import Image, ImageTk

# Locale settings
LOCALE_LOCK = threading.Lock()
ui_locale = 'en_IN.UTF-8'
time_format = 12
date_format = "%b %d, %Y"
news_country_code = 'in'

# Weather API Settings (OpenWeatherMap)
weather_api_token = '4dadecffa6e688e4a45f8fae8bf6ad0b'
latitude = '18.5256'
longitude = '73.8456'

# UI sizes
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18

icon_lookup = {
    'clear': "assets/Sun.png",
    'clouds': "assets/Cloud.png",
    'rain': "assets/Rain.png",
    'drizzle': "assets/Rain.png",
    'thunderstorm': "assets/Storm.png",
    'snow': "assets/Snow.png",
    'mist': "assets/Haze.png",
    'fog': "assets/Haze.png",
    'haze': "assets/Haze.png",
    'smoke': "assets/Wind.png"
}


@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            if name in locale.locale_alias:
                yield locale.setlocale(locale.LC_ALL, name)
            else:
                raise locale.Error(f"Locale '{name}' not supported.")
        finally:
            locale.setlocale(locale.LC_ALL, saved)


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.time1 = ''
        self.day_of_week1 = ''
        self.date1 = ''

        self.timeLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)

        self.dayOWLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)

        self.dateLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)

        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            time2 = time.strftime('%I:%M %p') if time_format == 12 else time.strftime('%H:%M')
            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)

            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)

            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)

            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)

        self.timeLbl.after(200, self.tick)


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.currently = ''
        self.icon = ''
        self.location = "Pune, MH"

        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)

        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)

        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)

        self.currentlyLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)

        self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)

        self.locationLbl = Label(self, text=self.location, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)

        self.get_weather()

    def get_weather(self):
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_token}&units=metric"
            r = requests.get(url)
            weather_obj = r.json()

            temp = int(weather_obj['main']['temp'])
            description = weather_obj['weather'][0]['description'].capitalize()
            icon_key = weather_obj['weather'][0]['main'].lower()
            city = weather_obj['name']
            country = weather_obj['sys']['country']

            temperature2 = f"{temp}°"
            forecast2 = description
            
            fp = open("Weather.json", "w")
            fp.write(str(weather_obj))
            fp.close()

            icon2 = icon_lookup.get(icon_key)

            if icon2:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.Resampling.LANCZOS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)
                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo

            self.temperatureLbl.config(text=temperature2)
            self.currentlyLbl.config(text=description)
            self.forecastLbl.config(text=forecast2)
            self.locationLbl.config(text=f"{city}, {country}")

        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get weather.")

        self.after(600000, self.get_weather)


class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'News'
        self.newsLbl = Label(self, text=self.title, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)

        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)

        self.get_headlines()

    def get_headlines(self):
        try:
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()

            url = f"https://news.google.com/news?ned={news_country_code}&output=rss"
            feed = feedparser.parse(url)

            for post in feed.entries[:5]:
                headline = NewsHeadline(self.headlinesContainer, post.title)
                headline.pack(side=TOP, anchor=W)
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get news.")

        self.after(600000, self.get_headlines)


class NewsHeadline(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.Resampling.LANCZOS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventNameLbl = Label(self, text=event_name, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)


class FullscreenWindow:
    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background='black')
        self.bottomFrame = Frame(self.tk, background='black')
        self.topFrame.pack(side=TOP, fill=BOTH, expand=YES)
        self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)

        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)

        self.news = News(self.bottomFrame)
        self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"


if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()
