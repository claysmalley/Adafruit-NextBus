import threading
import time
import requests
import json
from pathlib import Path

class weather:
	interval = 120 # Default polling interval = 2 minutes
	initSleep = 0 # Stagger polling threads to avoid load spikes
	config = {}
	with open(Path(__file__).with_name('config.json')) as config_file:
		config = json.load(config_file)
	
	# Each object spawns its own thread and will perform
	# periodic server queries in the background, which can then be
	# read via the weather, forecast and hourly properties.
	def __init__(self):
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
			weather_result = weather.req_weather()
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
			forecast_result = weather.req_forecast()
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
			hourly_result = weather.req_hourly()
			if hourly_result is None: return # Connection error
			self.hourly = hourly_result

			self.lastQueryTime = time.time()
			time.sleep(weather.interval)

	# Periodically get bus predictions from server
	def bus_thread(self):
		initSleep = weather.initSleep
		weather.initSleep += 5 # Thread staggering may
		time.sleep(initSleep) # drift over time, no problem
		while True:
			bus_result = weather.req_bus()
			if bus_result is None: return # Connection error
			self.bus = bus_result

			self.lastQueryTime = time.time()
			time.sleep(weather.interval)

	# Periodically get train predictions from server
	def train_thread(self):
		initSleep = weather.initSleep
		weather.initSleep += 5 # Thread staggering may
		time.sleep(initSleep) # drift over time, no problem
		while True:
			train_result = weather.req_train()
			if train_result is None: return # Connection error
			self.train = train_result

			self.lastQueryTime = time.time()
			time.sleep(weather.interval)

	@staticmethod
	def req_weather():
		json_result = None
		url = ''.join((
		 'https://api.weather.gov/gridpoints/',
		 weather.config['NWS_REGION'],
		 '/',
		 weather.config['NWS_GRIDPOINT_LAT'],
		 ',',
		 weather.config['NWS_GRIDPOINT_LON']
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	@staticmethod
	def req_forecast():
		json_result = None
		url = ''.join((
		 'https://api.weather.gov/gridpoints/',
		 weather.config['NWS_REGION'],
		 '/',
		 weather.config['NWS_GRIDPOINT_LAT'],
		 ',',
		 weather.config['NWS_GRIDPOINT_LON'],
		 '/forecast'
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	@staticmethod
	def req_hourly():
		json_result = None
		url = ''.join((
		 'https://api.weather.gov/gridpoints/',
		 weather.config['NWS_REGION'],
		 '/',
		 weather.config['NWS_GRIDPOINT_LAT'],
		 ',',
		 weather.config['NWS_GRIDPOINT_LON'],
		 '/forecast/hourly'
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	@staticmethod
	def req_bus():
		json_result = None
		url = ''.join((
		 'https://www.ctabustracker.com/bustime/api/v2/getpredictions?format=json&key=',
		 weather.config['CTA_BUS_API_KEY'],
		 '&stpid=',
		 weather.config['CTA_BUS_STOPS']
		 ))
		try:
			connection = requests.get(url)
			if connection.status_code == 200:
				json_result = connection.json()
		finally:
			return json_result

	@staticmethod
	def req_train():
		json_result = None
		url = ''.join((
		 'https://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?outputType=JSON&key=',
		 weather.config['CTA_TRAIN_API_KEY'],
		 '&mapid=',
		 weather.config['CTA_TRAIN_STOPS']
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

