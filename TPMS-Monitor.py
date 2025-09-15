#########################################################################
# Simple Python3 TPMS scanner                                           #
# Sept 2025 ride                                                        #
# Originally based on "tpms-bleak.py" at https://github.com/andi38/TPMS #
# Added QT window and other functionality                               #
# Lots of fixes and help from ChatGPT actually.                         #
# It was useful. https://chatgpt.com/g/g-cKrO5THiU-python-code-fixer    #
#########################################################################

#basic system stuff and async modules
import sys, asyncio, qasync

#To Draw the GUI
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDesktopWidget
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QRect

#Bluetooth BLE
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

#import pprint

class sensors:
	########################################
	# Update the sensor MAC addresses here #
	########################################
	FL_SENSOR = "4B:A8:00:00:4F:43" #Front Left
	FR_SENSOR = "4B:9D:00:00:4A:2A" #Front Right
	RL_SENSOR = "11:22:33:44:55:66" #Rear Left
	RR_SENSOR = "AA:BB:CC:DD:EE:FF" #Rear Right

def parse_sensor_data(advertisement_data): #Parse the data RX'd from the sensors
	mfdata = advertisement_data.manufacturer_data
	for data1, list2 in mfdata.items():
		list1 = [data1 % 256, data1 // 256]
		ldata = list1 + list(list2)

		batt = ldata[1] / 10
		temp = ldata[2]
		press = (((ldata[3] * 256) | (ldata[4])) - 145) / 10.0  # in psi

		return {
			"BATT": batt,
			"TEMPc": temp,
			"TEMPf": round((temp * (9 / 5)) + 32, 2),
			"BAR": round(press / 14.504, 1),
			"PSI": round(press, 1),
			"KPA": round((press / 14.504) * 10, 1),
			#"KPA": round(press * 6.895, 2),
		}
	return None

#BLE Scanner function
async def ble_device_scanner(window):
	try:
		# Mapping MAC addresses to tire positions
		mac_to_tire = {
			sensors.FL_SENSOR: "FL",
			sensors.FR_SENSOR: "FR",
			sensors.RL_SENSOR: "RL",
			sensors.RR_SENSOR: "RR",
		}

		def found(device: BLEDevice, advertisement_data: AdvertisementData):
			tire = mac_to_tire.get(device.address)
			if tire:
				parsed = parse_sensor_data(advertisement_data)
				if parsed:
					window.tire_info[tire].update(parsed)
					window.activity = 1
					window.activity_timer.start(750)
					window.trigger_repaint()

		# Start BT scanning
		scanner = BleakScanner(detection_callback=found)
		await scanner.start()

		# Keep the scanner alive
		while True:
			await asyncio.sleep(10.0)
			window.trigger_repaint()

	except asyncio.CancelledError:
		await scanner.stop()
		raise

#This draws the window
class MainWindow(QMainWindow):
			def __init__(self, loop):
				super().__init__()
				self.loop = loop
				self.setGeometry(0, 800, 350, 400) #Stick the Window in the bottom left corner
				self.pos1 = [0,0]
				self.pos2 = [0,0]
				self.setWindowTitle("Truckputer TPMS")
				self.setWindowIcon(QIcon("./TPMSicon.png"))
				self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #removes the window's top bar and borders
				self.ble_task = None

				self.activity = 0

				#Reset the activity light? (ChatGPT help)
				self.activity_timer = QtCore.QTimer()
				self.activity_timer.setSingleShot(True)
				self.activity_timer.timeout.connect(self.reset_activity)

				self.tire_info = {
					"UNITS":"PSI",
					"FL":{"BATT":0, "TEMPf":0, "TEMPc":32, "PSI":0, "BAR":0.0, "KPA":0},
					"FR":{"BATT":0, "TEMPf":0, "TEMPc":32, "PSI":0, "BAR":0.0, "KPA":0},
					"RL":{"BATT":0, "TEMPf":0, "TEMPc":32, "PSI":0, "BAR":0.0, "KPA":0},
					"RR":{"BATT":0, "TEMPf":0, "TEMPc":32, "PSI":0, "BAR":0.0, "KPA":0},
					"SP":{"BATT":0, "TEMPf":0, "TEMPc":32, "PSI":0, "BAR":0.0, "KPA":0}
				}

				self.unitsButton = QPushButton("PSI", self)
				self.unitsButton.setFont(QFont("Noto Sans", 20, QFont.Bold))
				self.unitsButton.clicked.connect(self.cycleUnits)
				self.unitsButton.setGeometry(145, 40, 60, 50)

			def reset_activity(self):
				self.activity = 0
				self.update()

			def drawVehicleFrame(self, qp): #Draws the basic vehicle wheels and axles
				frtLeft = QRect(15,15,100,155)
				frtRight = QRect(235,15,100,155)
				rearLeft = QRect(15,215,100,155)
				rearRight = QRect(235,215,100,155)

				#Store the rectangles so they are easier to use later
				self.tireRects = {
					"FL": frtLeft,
					"FR": frtRight,
					"RL": rearLeft,
					"RR": rearRight,
				}

				for rect in self.tireRects.values():
					qp.drawRect(rect)

				#front "axle"
				qp.drawLine(102,95,250,95)
				#rear "axle"
				qp.drawLine(102,295,250,295)
				#"driveline"
				qp.drawLine(175,95,175,295)

				#make a little circle for the rear diff
				#(makes it easy to tell front and rear! ;-) )
				qp.setBrush(QBrush(Qt.white, Qt.SolidPattern))
				qp.drawEllipse(165,285,20,20) #x,y,width,height


			def activityIndicator(self, qp): #draw the little activity light
				if self.activity == 1:
					qp.setBrush(QBrush(Qt.green, Qt.SolidPattern))
				else:
					qp.setBrush(QBrush(Qt.NoBrush))
				qp.drawEllipse(170,10,10,10)


			def drawTireInfo(self, qp, rect, tire, units): #draw the info in each "wheel"
				upperText = (Qt.AlignTop | Qt.AlignHCenter)
				centerText = Qt.AlignCenter
				bottomText = (Qt.AlignBottom | Qt.AlignHCenter)
				qp.setFont(QFont("Noto Sans", 30, QFont.Bold))
				value = tire[units]

				#Check pressure and change color based on range
				#PSI
				if units == "PSI":
					if 30 <= value <= 40:
						qp.setPen(QtCore.Qt.GlobalColor.green)
					elif 20 <= value < 30:
						qp.setPen(QtCore.Qt.GlobalColor.yellow)
					else:
						qp.setPen(QtCore.Qt.GlobalColor.red)
				#BAR
				if units == "BAR":
					if 2.1 <= value <= 2.8:
						qp.setPen(QtCore.Qt.GlobalColor.green)
					elif 1.4 <= value < 2.1:
						qp.setPen(QtCore.Qt.GlobalColor.yellow)
					else:
						qp.setPen(QtCore.Qt.GlobalColor.red)
				#KPA
				if units == "KPA":
					qp.setFont(QFont("Noto Sans", 21, QFont.Bold))
					if 210 <= value <= 280:
						qp.setPen(QtCore.Qt.GlobalColor.green)
					elif 140 <= value < 210:
						qp.setPen(QtCore.Qt.GlobalColor.yellow)
					else:
						qp.setPen(QtCore.Qt.GlobalColor.red)

				qp.drawText(rect, upperText, str(value))

				qp.setFont(QFont("Noto Sans", 11, QFont.Bold))
				qp.setPen(QtCore.Qt.GlobalColor.white)
				qp.drawText(rect, bottomText, f"{tire['TEMPf']}°F\n{tire['TEMPc']}°C\n{tire['BATT']}v\n")

			def paintEvent(self, event):
				width = self.pos2[0]-self.pos1[0]
				height = self.pos2[1]-self.pos1[1]
				gradient = QtGui.QLinearGradient()
				gradient.setColorAt(0, QtCore.Qt.red)
				gradient.setColorAt(1, QtCore.Qt.green)

				qp = QPainter(self)

				qp.setPen(QtCore.Qt.GlobalColor.white)

				######################
				# Draw the "Vehicle" #
				######################

				#Where to put the "Wheels"
				#QRect(x,y of upper left corner, width, height)
				frtLeft = QRect(15,15,100,155)
				frtRight = QRect(235,15,100,155)
				rearLeft = QRect(15,215,100,155)
				rearRight = QRect(235,215,100,155)

				#Draw the "wheels"
				qp.drawRect(frtLeft)
				qp.drawRect(frtRight)
				qp.drawRect(rearLeft)
				qp.drawRect(rearRight)


				#front "axle"
				qp.drawLine(102,95,250,95)
				#rear "axle"
				qp.drawLine(102,295,250,295)
				#"driveline"
				qp.drawLine(175,95,175,295)

				#make a little circle for the rear diff
				#(makes it easy to tell front and rear! ;-) )
				qp.setBrush(QBrush(Qt.white, Qt.SolidPattern))
				qp.drawEllipse(165,285,20,20) #x,y,width,height
				#############################
				# End Drawing the "Vehicle" #
				#############################

				#Activity indicator
				if self.activity == 1:
					qp.setBrush(QBrush(Qt.green, Qt.SolidPattern))
				else:
					qp.setBrush(QBrush(Qt.NoBrush))
				qp.drawEllipse(170,10,10,10)

				#################################
				# Drawing the Values from       #
				# the Sensors Onto the "Wheels" #
				#################################

				#Setup some different ways to align the text
				upperText = (Qt.AlignTop | Qt.AlignHCenter)
				centerText = Qt.AlignCenter
				centerLeft = (Qt.AlignVCenter | Qt.AlignLeft)
				centerRight = (Qt.AlignVCenter | Qt.AlignRight)
				bottomText = (Qt.AlignBottom | Qt.AlignHCenter)

				##########################
				# Fill out the tire Info #
				##########################
				units = self.tire_info['UNITS']
				self.drawTireInfo(qp, frtLeft, self.tire_info['FL'], units)
				self.drawTireInfo(qp, frtRight, self.tire_info['FR'], units)
				self.drawTireInfo(qp, rearLeft, self.tire_info['RL'], units)
				self.drawTireInfo(qp, rearRight, self.tire_info['RR'], units)

				#Stop drawing the Vehicle and other stuff.
				qp.end()

			#Repaint window?
			def trigger_repaint(self):
				self.update()

			def showEvent(self, event):
				"""Start BLE scanner when window is shown"""
				if self.ble_task is None or self.ble_task.done():
					self.ble_task = self.loop.create_task(ble_device_scanner(self))
					#print("scan disabled...")
				super().showEvent(event)

			def closeEvent(self, event):
				#Stop BLE scanner when window is closed
				if self.ble_task and not self.ble_task.done():
					self.ble_task.cancel()
					#print("scan cancelled...")
				super().closeEvent(event)
#for debugging				pprint.pprint(self.tire_info)

			def cycleUnits(self):
				current = self.tire_info['UNITS']
				order = ["PSI", "BAR", "KPA"]
				nextUnit = order[(order.index(current) + 1) % len(order)]
				self.tire_info['UNITS'] = nextUnit
				self.unitsButton.setText(f"{nextUnit}")
				self.trigger_repaint()
#				print(self.tire_info)

async def main_window():
	app = QApplication(sys.argv)
	loop = qasync.QEventLoop(app)
	asyncio.set_event_loop(loop)

	window = MainWindow(loop)

	#Quit button for when we remove title bar, etc.
	quitButton = QPushButton("Quit", window)
	quitButton.setFont(QFont("Noto Sans", 14, QFont.Bold))
	quitButton.clicked.connect(window.close)
	quitButton.setGeometry(145, 345, 60, 50)

	window.show()
	window.trigger_repaint()

	# ensure coroutine is "awaited" before run_forever blocks
	#no idea what that means, but thanks ChatGPT!
	await asyncio.sleep(0)

	with loop:
		loop.run_forever()

if __name__ == "__main__":
	asyncio.run(main_window())
