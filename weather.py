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
		t = threading.Thread(target=self.thread)
		t.daemon = True
		t.start()

	# Periodically get forecast from server
	def thread(self):
		initSleep = weather.initSleep
		weather.initSleep += 5 # Thread staggering may
		time.sleep(initSleep) # drift over time, no problem
		while True:
			weather_result = weather.req_weather(self.data)
			if weather_result is None: return # Connection error
			self.weather = weather_result

			forecast_result = weather.req_forecast(self.data)
			if forecast_result is None: return # Connection error
			self.forecast = forecast_result

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
		print(''.join((url, ': Requesting...')))
		try:
			connection = requests.get(url)
			print(''.join((url, ': Success')))
			json_result = connection.json()
		except:
			print(''.join((url, ': Failure')))
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
		print(''.join((url, ': Requesting...')))
		try:
			connection = requests.get(url)
			print(''.join((url, ': Success')))
			json_result = connection.json()
		except:
			print(''.join((url, ': Failure')))
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
		print(''.join((url, ': Requesting...')))
		try:
			connection = requests.get(url)
			print(''.join((url, ': Success')))
			json_result = connection.json()
		except:
			print(''.join((url, ': Failure')))
		finally:
			return json_result

	# Set polling interval (seconds)
	@staticmethod
	def setInterval(i):
		interval = i

