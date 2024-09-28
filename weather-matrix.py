#!/usr/bin/env python3

# NextBus scrolling marquee display for Adafruit RGB LED matrix (64x32).
# Requires rgbmatrix.so library: github.com/adafruit/rpi-rgb-led-matrix

import atexit
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import math
import os
import time
from weather import weather
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configurable stuff ---------------------------------------------------------

width          = 64  # Matrix size (pixels) -- change for different matrix
height         = 32  # types (incl. tiling).  Other code may need tweaks.
matrixOptions = RGBMatrixOptions()
matrixOptions.hardware_mapping = 'adafruit-hat'
matrix         = RGBMatrix(32, 2, options = matrixOptions) # rows, chain length
fps            = 20  # Scrolling speed (ish)

labelColor     = (127, 127, 127)
nightColor     = (100, 0, 0)
temp30Color = (214, 113, 217)
temp40Color = (50, 40, 251)
temp50Color = (5, 189, 230)
temp60Color = (1, 210, 100)
temp70Color = (120, 208, 3)
temp80Color = (255, 250, 0)
temp90Color = (255, 110, 0)
temp100Color = (255, 10, 0)
precipColor = (110, 110, 240)
leaveNowColor = (255, 10, 0)
leaveSoonColor = (255, 250, 0)

# TrueType fonts are a bit too much for the Pi to handle -- slow updates and
# it's hard to get them looking good at small sizes.  A small bitmap version
# of Helvetica Regular taken from X11R6 standard distribution works well:
font           = ImageFont.load(os.path.dirname(os.path.realpath(__file__))
	+ '/helvR08.pil')
fontYoffset    = -2  # Scoot up a couple lines so descenders aren't cropped


# Main application -----------------------------------------------------------

# Drawing takes place in offscreen buffer to prevent flicker
image       = Image.new('RGB', (width, height))
draw        = ImageDraw.Draw(image)
currentTime = 0.0
prevTime    = 0.0

hour = int(time.strftime('%H'))
nightMode = hour < 7 or hour >= 21

# Clear matrix on exit.  Otherwise it's annoying if you need to break and
# fiddle with some code while LEDs are blinding you.
def clearOnExit():
	matrix.Clear()

atexit.register(clearOnExit)

def celsiusToFahrenheit(temperature):
	return round(temperature * 9 / 5 + 32)

def colorFromFahrenheit(temperature):
	if temperature is None:
		return labelColor
	color = temp30Color
	colorSwitch = min(10, temperature // 10)
	if colorSwitch == 4:
		color = temp40Color
	elif colorSwitch == 5:
		color = temp50Color
	elif colorSwitch == 6:
		color = temp60Color
	elif colorSwitch == 7:
		color = temp70Color
	elif colorSwitch == 8:
		color = temp80Color
	elif colorSwitch == 9:
		color = temp90Color
	elif colorSwitch == 10:
		color = temp100Color
	return color

def colorFromMinutes(prediction, walkTime):
	whenToLeave = prediction - walkTime
	color = labelColor
	if whenToLeave < 15:
		color = leaveSoonColor
	if whenToLeave < 5:
		color = leaveNowColor
	return color

class tile:
	def __init__(self, x, y, text, color=labelColor):
		self.x = x
		self.y = y
		self.setText(text)
		self.color = color

	def update(self):
		pass

	def setText(self, text):
		if text is None:
			self.text = '??'
		else:
			self.text = text

	def draw(self):
		self.update()
		x     = self.x
		label = str(self.text)
		color = nightColor if nightMode else self.color
		draw.text((x, self.y + fontYoffset), label, font=font,
			fill=color)

class humidityForecastTile(tile):
	def __init__(self, x, y, weatherInfo, color=labelColor, period=0):
		self.weatherInfo = weatherInfo
		self.period = period
		super().__init__(x, y, None, color)

	def update(self):
		if self.weatherInfo.forecast is None:
			self.setText(None)
		else:
			self.setText(''.join((
				str(self.weatherInfo.forecast['properties']['periods'][self.period]['relativeHumidity']['value']), '%'))
				)

class precipitationForecastTile(tile):
	def __init__(self, x, y, weatherInfo, color=precipColor, period=0):
		self.weatherInfo = weatherInfo
		self.period = period
		super().__init__(x, y, None, color)

	def update(self):
		forecastPart = '??'

		if self.weatherInfo.forecast is not None:
			forecastPart = self.weatherInfo.forecast['properties']['periods'][0]['probabilityOfPrecipitation']['value'] or 0

		self.setText(''.join((str(forecastPart), '%')))

class precipitationHourlyTile(tile):
	def __init__(self, x, y, weatherInfo, color=precipColor, period=0):
		self.weatherInfo = weatherInfo
		self.period = period
		super().__init__(x, y, None, color)

	def update(self):
		hourlyPart = '??'

		if self.weatherInfo.hourly is not None:
			hourlyPart = self.weatherInfo.hourly['properties']['periods'][0]['probabilityOfPrecipitation']['value'] or 0

		self.setText(''.join(('(', str(hourlyPart), '%)')))

class temperatureTile(tile):
	def __init__(self, x, y, temperature):
		self.setText(temperature)
		super().__init__(x, y, temperature, self.color)

	def setText(self, temperature):
		self.color = colorFromFahrenheit(temperature)
		if temperature is None:
			self.text = '??'
		elif temperature >= 100:
			self.text = temperature
		else:
			self.text = ''.join((str(temperature), '° '))

class temperatureForecastTile(temperatureTile):
	def __init__(self, x, y, weatherInfo, period=0):
		self.weatherInfo = weatherInfo
		self.period = period
		super().__init__(x, y, None)
	
	def update(self):
		if self.weatherInfo.forecast is None:
			self.setText(None)
		else:
			self.setText(
				self.weatherInfo.forecast['properties']['periods'][self.period]['temperature']
				)

class predictionTile(tile):
	def __init__(self, x, y, predictions, walkTime=0):
		self.x = x
		self.y = y
		self.walkTime = walkTime
		self.setText(predictions)

	def setText(self, predictions):
		if len(predictions) == 0:
			self.color = labelColor
			self.text = '--'
		else:
			self.color = colorFromMinutes(predictions[0], self.walkTime)
			self.text = ','.join((str(prediction) for prediction in predictions))

weatherInfo = weather()

tileList = [
	tile(0, 0, 'T'),
	temperatureForecastTile(20, 0, weatherInfo, 0),
	temperatureForecastTile(42, 0, weatherInfo, 1),
	tile(0, 8, 'P'),
	precipitationForecastTile(20, 8, weatherInfo),
	precipitationHourlyTile(39, 8, weatherInfo),
	# predictionTile(5, 16, (6, 8), 3),
	]
 
# Initialization done; loop forever ------------------------------------------
while True:

	# Clear background
	draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

	for t in tileList:
		if t.x < width:        # Draw tile if onscreen
			t.draw()

	# Try to keep timing uniform-ish; rather than sleeping a fixed time,
	# interval since last frame is calculated, the gap time between this
	# and desired frames/sec determines sleep time...occasionally if busy
	# (e.g. polling server) there'll be no sleep at all.
	currentTime = time.time()
	timeDelta   = (1.0 / fps) - (currentTime - prevTime)
	if(timeDelta > 0.0):
		time.sleep(timeDelta)
	prevTime = currentTime

	# Offscreen buffer is copied to screen
	matrix.SetImage(image, 0, 0)
