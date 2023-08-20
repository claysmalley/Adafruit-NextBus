import threading
import time
import requests

class weather:
	interval = 120 # Default polling interval = 2 minutes
	initSleep = 0 # Stagger polling threads to avoid load spikes

	# object initializer. 1 parameter, a 3-element tuple:
	# 1. a National Weather Service region code, 3 letters
	# 2. the gridpoint latitude
	# 3. the gridpoint longitude
	# Each object spawns its own thread and will perform
	# periodic server queries in the background, which can then be
	# read via the weather, forecast and hourly properties.
	def __init__(self, data):
		self.data = data
		self.weather = None
		self.forecast = None
		self.hourly = None
		self.lastQueryTime = time.time()
		w = threading.Thread(target=self.weather_thread)
		w.daemon = True
		w.start()
		f = threading.Thread(target=self.forecast_thread)
		f.daemon = True
		f.start()
		h = threading.Thread(target=self.hourly_thread)
		h.daemon = True
		h.start()

	# Periodically get weather from server
	def weather_thread(self):
		initSleep = weather.initSleep
		weather.initSleep += 5 # Thread staggering may
		time.sleep(initSleep) # drift over time, no problem
		while True:
			weather_result = weather.req_weather(self.data)
			if weather_result is None: return # Connection error
			self.weather = weather_result

			self.lastQueryTime = time.time()
			time.sleep(weather.interval)

	# Periodically get forecast from server
	def forecast_thread(self):
		initSleep = weather.initSleep
		weather.initSleep += 5 # Thread staggering may
		time.sleep(initSleep) # drift over time, no problem
		while True:
			forecast_result = weather.req_forecast(self.data)
			if forecast_result is None: return # Connection error
			self.forecast = forecast_result

			self.lastQueryTime = time.time()
			time.sleep(weather.interval)

	# Periodically get hourly forecast from server
	def hourly_thread(self):
		initSleep = weather.initSleep
		weather.initSleep += 5 # Thread staggering may
		time.sleep(initSleep) # drift over time, no problem
		while True:
			hourly_result = weather.req_hourly(self.data)
			if hourly_result is None: return # Connection error
			self.hourly = hourly_result

			self.lastQueryTime = time.time()
			time.sleep(weather.interval)

	@staticmethod
	def req_weather(data):
		json_result = None
		url = ''.join((
		 'https://api.weather.gov/gridpoints/',
		 data[0],
		 '/',
		 data[1],
		 ',',
		 data[2]
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	@staticmethod
	def req_forecast(data):
		json_result = None
		url = ''.join((
		 'https://api.weather.gov/gridpoints/',
		 data[0],
		 '/',
		 data[1],
		 ',',
		 data[2],
		 '/forecast'
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	@staticmethod
	def req_hourly(data):
		json_result = None
		url = ''.join((
		 'https://api.weather.gov/gridpoints/',
		 data[0],
		 '/',
		 data[1],
		 ',',
		 data[2],
		 '/forecast/hourly'
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	# Set polling interval (seconds)
	@staticmethod
	def setInterval(i):
		interval = i

