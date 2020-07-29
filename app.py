import requests
import urllib
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from threading import Thread
from os import getenv


class GUI:
    def __init__(self):
        self.COUNTRY_API_URL = "https://restcountries.eu/rest/v2/all"
        self.WEATHER_API_URL = f"http://api.weatherstack.com/current"

        self.root = tk.Tk()
        self.root.title("Weather")
        self.Title = tk.Label(self.root, text="Weather for Capitals", font=("Comic Sans", 16))
        self.output = ScrollableFrame(self.root, bg="green")
        self.bottomButton = tk.Button(self.root, text="Refresh Data")

        self.Title.pack(side="top")
        self.output.pack()
        self.bottomButton.pack(side="bottom", fill="x")

        # List of output elements to be destroyed when the window is updated
        self.outputElements = []

        self.mainScreen()

        self.root.mainloop()

    def mainScreen(self):
        def createCountryElement(countryData):
            countryFrame = tk.Frame(self.output.scrollable_frame)
            countryFrame.pack(fill="x")
            self.outputElements.append(countryFrame)
            tk.Label(countryFrame, text=countryData['name']).pack(side="left")
            tk.Button(countryFrame, text="Show", command=lambda: self.weatherScreen(countryData)).pack(side="right")

        def handleData(data, error=None):
            if error: return messagebox.showerror('Error!', error)
    
            # Destroy old elements
            if self.outputElements: [element.destroy() for element in self.outputElements]

            self.Title['text'] = f"Weather for Capitals"
            self.bottomButton['text'] = "Refresh Data"
            self.bottomButton['command'] = lambda: self.mainScreen()

            [createCountryElement(country) for country in data]

        Thread(target=handleRequest, args=(self.COUNTRY_API_URL, handleData)).start()

    def weatherScreen(self, countryData):
        def createWeatherWidgets(weatherData, error=None):
            if error: return messagebox.showerror('Error!', error)
            if self.outputElements: [element.destroy() for element in self.outputElements]

            self.Title['text'] = f"Weather for {countryData['capital']}"
            self.bottomButton['text'] = "Go Back"
            self.bottomButton['command'] = lambda: self.mainScreen()

            DataFrame = tk.Frame(self.output.scrollable_frame)
            DataFrame.pack(anchor="sw", side="top", fill="x")
            self.outputElements.append(DataFrame)

            displayData = [
                f"Country Name:  {countryData['name']}",
                f"Country's Capital:  {countryData['capital']}",
                f"Population:  {countryData['population']}",
                f"Timezone(s):  {', '.join(countryData['timezones'])}",
                f"Currencie(s):  {', '.join([i['name'] for i in countryData['currencies']])}",
                f"Language(s):  {', '.join([i['name'] for i in countryData['languages']])}",
                f"Calling Code:  {', '.join(countryData['callingCodes'])}",
                f"Current Time:  {weatherData['location']['localtime']}; {'Daytime' if weatherData['current']['is_day'] else 'NightTime'}",
                f"Temperature:  {weatherData['current']['temperature']}",
                f"Feels Like:  {weatherData['current']['feelslike']}",
                f"Wind:  {weatherData['current']['wind_speed']} km/hr; {weatherData['current']['wind_degree']} degrees {weatherData['current']['wind_dir']}",
                f"Pressure:  {weatherData['current']['pressure']}",
                f"Humidity:  {weatherData['current']['humidity']}",
                f"Weather Description:  {', '.join(weatherData['current']['weather_descriptions'])}",
                f"Precipitation:  {weatherData['current']['precip']}mm",
            ]

            [tk.Label(DataFrame, text=dataPoint).pack(anchor="w") for dataPoint in displayData]

        urlparams = urllib.parse.urlencode({'access_key': API_KEY, 'query': countryData['name']})
        url = f"{self.WEATHER_API_URL}?{urlparams}"
        Thread(target=handleRequest, args=(url, createWeatherWidgets)).start()


def handleRequest(url, callback=None):
    try:
        res = requests.get(url)
        if res.status_code != 200: raise requests.exceptions.InvalidURL('Could not connect to server')
        data = res.json()
        if callback: callback(data)
    except Exception as e:
        errorMessage = f"{e.__class__.__name__}: {e}"
        print(errorMessage)
        if callback: callback(None, errorMessage)


# https://blog.tecladocode.com/tkinter-scrollable-frames/
# Scrollable frame class
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(width=100)
        self.scrollable_frame.pack(side="left")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


if __name__ == '__main__':
    # Load Env variables & Check if it is set
    if getenv('API_KEY') is None: load_dotenv()
    API_KEY = getenv('API_KEY')
    if API_KEY is None: raise FileNotFoundError("Add your API key to the .env")
    GUI()
