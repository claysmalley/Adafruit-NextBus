import threading
import time
import urllib
import json

class weather:
	interval  = 120 # Default polling interval = 2 minutes
	initSleep = 0   # Stagger polling threads to avoid load spikes

    # object initializer. 1 parameter, a 3-element tuple:
    # 1. a National Weather Service region code, 3 letters
    # 2. the gridpoint latitude
    # 3. the gridpoint longitude
	# Each object spawns its own thread and will perform
	# periodic server queries in the background, which can then be
	# read via the forecast[] list.
	def __init__(self, data):
		self.data          = data
		self.weather   = None
		self.forecast   = None
		self.hourly   = None
		self.lastQueryTime = time.time()
		t                  = threading.Thread(target=self.thread)
		t.daemon           = True
		t.start()

	# Periodically get forecast from server
	def thread(self):
		initSleep          = weather.initSleep
		weather.initSleep += 5   # Thread staggering may
		time.sleep(initSleep)    # drift over time, no problem
		while True:
			json_result = weather.req(data)
			if json_result['weather'] is None: return    # Connection error
			if json_result['forecast'] is None: return   # Connection error
			if json_result['hourly'] is None: return     # Connection error
			self.lastQueryTime = time.time()
			self.weather = json_result['weather']
			self.forecast = json_result['forecast']
			self.hourly = json_result['hourly']
			time.sleep(weather.interval)

	# Open URL, send request, read & parse JSON response
	@staticmethod
	def req(data):
        json_result = {'weather': None, 'forecast': None, 'hourly': None}
		try:
			connection = urllib.urlopen(
			  'https://api.weather.gov/gridpoints/' + data[0] + '/' + data[1] + ',' + data[2])
			raw = connection.read()
			connection.close()
			json_result['weather'] = json.loads(raw)

			time.sleep(5)
			connection = urllib.urlopen(
			  'https://api.weather.gov/gridpoints/' + data[0] + '/' + data[1] + ',' + data[2] + '/forecast')
			raw = connection.read()
			connection.close()
			json_result['forecast'] = json.loads(raw)

			time.sleep(5)
			connection = urllib.urlopen(
			  'https://api.weather.gov/gridpoints/' + data[0] + '/' + data[1] + ',' + data[2] + '/forecast/hourly')
			raw = connection.read()
			connection.close()
			json_result['hourly'] = json.loads(raw)
		finally:
			return json_result

	# Set polling interval (seconds)
	@staticmethod
	def setInterval(i):
		interval = i

