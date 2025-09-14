'''
Simple Python3 TPMS scanner
Sept 2025 ride
Originally based on "tpms-bleak.py" at https://github.com/andi38/TPMS
Added QT window and other functionality
Lots of fixes and help from ChatGPT actually.
It was useful. https://chatgpt.com/g/g-cKrO5THiU-python-code-fixer
'''

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

#This must be a "class" like this so that the "match" (below) happens correctly
#match on just FL_SENSOR will never be true, but match on sensors.FL_SENSOR and it does match the string?
#yeah weird, go figure! something with how python works
class sensors:
	########################################
	# Update the sensor MAC addresses here #
	########################################
	FL_SENSOR = "4B:A8:00:00:4F:43" #Front Left
	FR_SENSOR = "4B:9D:00:00:4A:2A" #Front Right
	RL_SENSOR = "" #Rear Left
	RR_SENSOR = "" #Rear Right
	#SP_SENSOR = "" #Spare (This may never get used, it does not spin)

#This is the BLE scanner using the "Bleak" python module.
async def ble_device_scanner(window):
	try:
		def found(device: BLEDevice, advertisement_data: AdvertisementData):
			match device.address:
				case sensors.FL_SENSOR:
#					print("Front Left detected")
					mfdata = advertisement_data.manufacturer_data
					for i in range(0,len(mfdata)):
						data1 = list(mfdata.keys())[i]
						list1 = [int(data1)%256,int(int(data1)/256)]
						list2 = list(mfdata[data1])
						ldata = list1 + list2
						batt = ldata[1]/10
						temp = ldata[2]
#						press = ((ldata[3]*256+ldata[4])-145)/145  # absolute pressure psi to bar (relative) (multiply by 14.504 to go back to psi)
						press = (((ldata[3]*256) | (ldata[4]))-145)/10.0 #in psi?

						window.tire_info['FL']['BATT'] = batt
						window.tire_info['FL']['TEMPc'] = temp
						window.tire_info['FL']['TEMPf'] = (temp*(9/5))+32
						window.tire_info['FL']['BAR'] = round(press/14.504, 2)
						window.tire_info['FL']['PSI'] = round(press, 1)
						window.tire_info['FL']['KPA'] = round(press*6.895, 2)

						window.activity = 1
						window.activity_timer.start(750)  # 3/4 second
						window.trigger_repaint()
#						print("B: ",batt, "  T: ",(temp*(9/5))+32,"F (",temp,"C)  p: ",round(press,2), sep='')

				case sensors.FR_SENSOR:
#					print("Front Right detected")
					mfdata = advertisement_data.manufacturer_data
					for i in range(0,len(mfdata)):
						data1 = list(mfdata.keys())[i]
						list1 = [int(data1)%256,int(int(data1)/256)]
						list2 = list(mfdata[data1])
						ldata = list1 + list2
						batt = ldata[1]/10
						temp = ldata[2]
#						press = ((ldata[3]*256+ldata[4])-145)/145  # absolute pressure psi to bar (relative) (multiply by 14.504 to go back to psi)
						press = (((ldata[3]*256) | (ldata[4]))-145)/10.0 #in psi?

						window.tire_info['FR']['BATT'] = batt
						window.tire_info['FR']['TEMPc'] = temp
						window.tire_info['FR']['TEMPf'] = (temp*(9/5))+32
						window.tire_info['FR']['BAR'] = round(press/14.504, 2)
						window.tire_info['FR']['PSI'] = round(press, 1)
						window.tire_info['FR']['KPA'] = round(press*6.895, 2)

						window.activity = 1
						window.activity_timer.start(750)  # 3/4 second
						window.trigger_repaint()
#						print("B: ",batt, "  T: ",(temp*(9/5))+32,"F (",temp,"C)  p: ",round(press,2), sep='')

				case sensors.RL_SENSOR:
#					print("Rear Left detected")
					mfdata = advertisement_data.manufacturer_data
					for i in range(0,len(mfdata)):
						data1 = list(mfdata.keys())[i]
						list1 = [int(data1)%256,int(int(data1)/256)]
						list2 = list(mfdata[data1])
						ldata = list1 + list2
						batt = ldata[1]/10
						temp = ldata[2]
#						press = ((ldata[3]*256+ldata[4])-145)/145  # absolute pressure psi to bar (relative) (multiply by 14.504 to go back to psi)
						press = (((ldata[3]*256) | (ldata[4]))-145)/10.0 #in psi?

						window.tire_info['RL']['BATT'] = batt
						window.tire_info['RL']['TEMPc'] = temp
						window.tire_info['RL']['TEMPf'] = (temp*(9/5))+32
						window.tire_info['RL']['BAR'] = round(press/14.504, 2)
						window.tire_info['RL']['PSI'] = round(press, 1)
						window.tire_info['RL']['KPA'] = round(press*6.895, 2)

						window.activity = 1
						window.activity_timer.start(750)  # 3/4 second
						window.trigger_repaint()
#						print("B: ",batt, "  T: ",(temp*(9/5))+32,"F (",temp,"C)  p: ",round(press,2), sep='')

				case sensors.RR_SENSOR:
#					print("Rear Right detected")
					mfdata = advertisement_data.manufacturer_data
					for i in range(0,len(mfdata)):
						data1 = list(mfdata.keys())[i]
						list1 = [int(data1)%256,int(int(data1)/256)]
						list2 = list(mfdata[data1])
						ldata = list1 + list2
						batt = ldata[1]/10
						temp = ldata[2]
#						press = ((ldata[3]*256+ldata[4])-145)/145  # absolute pressure psi to bar (relative) (multiply by 14.504 to go back to psi)
						press = (((ldata[3]*256) | (ldata[4]))-145)/10.0 #in psi?

						window.tire_info['RR']['BATT'] = batt
						window.tire_info['RR']['TEMPc'] = temp
						window.tire_info['RR']['TEMPf'] = (temp*(9/5))+32
						window.tire_info['RR']['BAR'] = round(press/14.504, 2)
						window.tire_info['RR']['PSI'] = round(press, 1)
						window.tire_info['RR']['KPA'] = round(press*6.895, 2)

						window.activity = 1
						window.activity_timer.start(750)  # 3/4 second
						window.trigger_repaint()
						print("B: ",batt, "  T: ",(temp*(9/5))+32,"F (",temp,"C)  p: ",round(press,2), sep='')

				case _: #Default Case
					#Just keep looking for the sensors
					pass

		#Start BT scanning for BLE devices with the above MAC addresses
		scanner = BleakScanner(detection_callback=found)
		await scanner.start()
#		print("Scanner started. Waiting for devices...")

		#This keeps something (the async thread?) alive? (ChatGPT fix)
		while True:
			await asyncio(sleep(10.0))
			window.trigger_repaint()

	#Kill scanner when window closes (ChatGPT fix)
	except asyncio.CancelledError:
#		print("BLE scanner cancelled. Cleaning up...")
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

			def reset_activity(self):
				self.activity = 0
				self.update()

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

				###
				#PSI "label" (maybe turn this into a button later that can change the pressure units)
				###
				#qp.setFont(QFont("Noto Sans", 16, QFont.Bold))
				#qp.drawText(100, 46, 50, 30, centerText, "PSI")

				###################
				# Front Left Info #
				###################
				qp.setFont(QFont("Noto Sans", 30, QFont.Bold))
				if 30 <= self.tire_info['FL']['PSI'] <= 40:
					qp.setPen(QtCore.Qt.GlobalColor.green)
				elif 20 <= self.tire_info['FL']['PSI'] < 30:
					qp.setPen(QtCore.Qt.GlobalColor.yellow)
				else:
					qp.setPen(QtCore.Qt.GlobalColor.red)
				qp.drawText(frtLeft, upperText, str(self.tire_info['FL']['PSI']))
				qp.setFont(QFont("Noto Sans", 11, QFont.Bold))
				qp.setPen(QtCore.Qt.GlobalColor.white)
				qp.drawText(frtLeft, centerText, "\n(" + str(self.tire_info['FL']['BAR']) + "b)\n(" + str(self.tire_info['FL']['KPA']) + "kPa)")
				## example: "0\N{DEGREE SIGN}F\n0v"
				qp.drawText(frtLeft, bottomText, str(self.tire_info['FL']['TEMPf']) + "\N{DEGREE SIGN}F " + str(self.tire_info['FL']['TEMPc']) + "\N{DEGREE SIGN}C\n" + str(self.tire_info['FL']['BATT']) + "v")

				####################
				# Front Right Info #
				####################
				qp.setFont(QFont("Noto Sans", 30, QFont.Bold))
				if 30 <= self.tire_info['FR']['PSI'] <= 40:
					qp.setPen(QtCore.Qt.GlobalColor.green)
				elif 20 <= self.tire_info['FR']['PSI'] < 30:
					qp.setPen(QtCore.Qt.GlobalColor.yellow)
				else:
					qp.setPen(QtCore.Qt.GlobalColor.red)
				qp.drawText(frtRight, upperText, str(self.tire_info['FR']['PSI']))
				qp.setFont(QFont("Noto Sans", 11, QFont.Bold))
				qp.setPen(QtCore.Qt.GlobalColor.white)
				qp.drawText(frtRight, centerText, "\n(" + str(self.tire_info['FR']['BAR']) + "b)\n(" + str(self.tire_info['FR']['KPA']) + "kPa)")
				qp.drawText(frtRight, bottomText, str(self.tire_info['FR']['TEMPf']) + "\N{DEGREE SIGN}F " + str(self.tire_info['FR']['TEMPc']) + "\N{DEGREE SIGN}C\n" + str(self.tire_info['FR']['BATT']) + "v")

				##################
				# Rear Left Info #
				##################
				qp.setFont(QFont("Noto Sans", 30, QFont.Bold))
				if 30 <= self.tire_info['RL']['PSI'] <= 40:
					qp.setPen(QtCore.Qt.GlobalColor.green)
				elif 20 <= self.tire_info['RL']['PSI'] < 30:
					qp.setPen(QtCore.Qt.GlobalColor.yellow)
				else:
					qp.setPen(QtCore.Qt.GlobalColor.red)
				qp.drawText(rearLeft, upperText, str(self.tire_info['RL']['PSI']))
				qp.setFont(QFont("Noto Sans", 11, QFont.Bold))
				qp.setPen(QtCore.Qt.GlobalColor.white)
				qp.drawText(rearLeft, centerText, "\n(" + str(self.tire_info['RL']['BAR']) + "b)\n(" + str(self.tire_info['RL']['KPA']) + "kPa)")
				qp.drawText(rearLeft, bottomText, str(self.tire_info['RL']['TEMPf']) + "\N{DEGREE SIGN}F " + str(self.tire_info['RL']['TEMPc']) + "\N{DEGREE SIGN}C\n" + str(self.tire_info['RL']['BATT']) + "v")

				###################
				# Rear Right Info #
				###################
				qp.setFont(QFont("Noto Sans", 30, QFont.Bold))
				if 30 <= self.tire_info['RR']['PSI'] <= 40:
					qp.setPen(QtCore.Qt.GlobalColor.green)
				elif 20 <= self.tire_info['RR']['PSI'] < 30:
					qp.setPen(QtCore.Qt.GlobalColor.yellow)
				else:
					qp.setPen(QtCore.Qt.GlobalColor.red)
				qp.drawText(rearRight, upperText, str(self.tire_info['RR']['PSI']))
				qp.setFont(QFont("Noto Sans", 11, QFont.Bold))
				qp.setPen(QtCore.Qt.GlobalColor.white)
				qp.drawText(rearRight, centerText, "\n(" + str(self.tire_info['RR']['BAR']) + "b)\n(" + str(self.tire_info['RR']['KPA']) + "kPa)")
				qp.drawText(rearRight, bottomText, str(self.tire_info['RR']['TEMPf']) + "\N{DEGREE SIGN}F " + str(self.tire_info['RR']['TEMPc']) + "\N{DEGREE SIGN}C\n" + str(self.tire_info['RR']['BATT']) + "v")

				#save spare for later, maybe we can figure something out
				#qp.drawText(100, 270, 50, 100, centerText, self.spareText)

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

async def main_window():
	app = QApplication(sys.argv)
	loop = qasync.QEventLoop(app)
	asyncio.set_event_loop(loop)

	window = MainWindow(loop)

	#Quit button for when we remove title bar, etc.
	quitButton = QPushButton("Quit", window)
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
