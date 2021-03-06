#!/usr/bin/env python
# Using Tkinter to create a GUI
import os
from multiprocessing import Process, Pipe
import roslib
roslib.load_manifest('se306_project1')
import rospy
from std_msgs.msg import String
#from se306_project1 import ResidentMsg
import Tkinter

callbackData = 'default'
STDIN = 0
STDOUT = 1
STDERR = 2

subscriber = None
# Subscribed value of health/hunger/boredom goes here
perc = 1
dataList = []
# We inherit from Tkinter.Tk, which is the base class for standard windows.
class ros_gui(Tkinter.Tk):
    # Constructor
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		# Keep a reference to our parent.
		self.parent = parent
		self.setupNode()
		self.initialize()

	def initialize(self):
		self.grid()
        
		# Image of Resident
		img = Tkinter.Button(self, text="Photo goes here", relief="raised", bitmap="error", height=80, width=80)
		img.grid(column=0, row=0)
        
		# Name of resident
		name = Tkinter.Label(self, text="Sean Kim", font=(20)) #Declare size of font and text
		name.grid(column=0, row=1)
        
		#====Start of statusFrame====#
        
		# Frame containing status of resident (health, hunger)
		statusFrame = Tkinter.Frame(self, bd=2, relief="groove", width=285, height=130)
		statusFrame.grid(column=0, row=2, padx=5, pady=2.5)
		statusFrame.grid_propagate(False)
        
		# Status title
		statusText = Tkinter.Label(statusFrame, text="Status", font=(18), anchor="center")
		statusText.grid(column=0, row=0, sticky="W")
        
		# Health
		healthText = Tkinter.Label(statusFrame, text="Health : ")
		healthText.grid(column=0, row=1, sticky="W")
        
		# Hunger
		hungerText = Tkinter.Label(statusFrame, text="Hunger : ")
		hungerText.grid(column=0, row=2, sticky="W")

		# Hunger
		boredomText = Tkinter.Label(statusFrame, text="Boredom : ")
		boredomText.grid(column=0, row=3, sticky="W")
        
		# Health Bar (Parent)
		self.healthBar = Tkinter.Canvas(statusFrame, bg="blue", height=16, width=200, highlightbackground="black")
		self.healthBar.grid(column=1, row=1, sticky="E", padx=3)
		# Health Bar (Filler)
		self.healthFiller = Tkinter.Canvas(statusFrame, bg="red", height=16, width=0, highlightbackground="black")
		self.healthFiller.grid(column=1, row=1, sticky="E", padx=3)
		# Hunger Bar (Parent)
		self.hungerBar = Tkinter.Canvas(statusFrame, bg="blue", height=16, width=200, highlightbackground="black")
		self.hungerBar.grid(column=1, row=2, sticky="E", padx=3)
		# Hunger Bar (Filler)
		self.hungerFiller = Tkinter.Canvas(statusFrame, bg="red", height=16, width=0, highlightbackground="black")
		self.hungerFiller.grid(column=1, row=2, sticky="E", padx=3)
        
		# Boredom Bar (Parent)
		self.boredomBar = Tkinter.Canvas(statusFrame, bg="blue", height=16, width=200, highlightbackground="black")
		self.boredomBar.grid(column=1, row=3, sticky="E", padx=3)
		# Boredom Bar (Filler)
		self.boredomFiller = Tkinter.Canvas(statusFrame, bg="red", height=16, width=0, highlightbackground="black")
		self.boredomFiller.grid(column=1, row=3, sticky="E", padx=3)
        # Position
		posText = Tkinter.Label(statusFrame, text="Position : ")
		posText.grid(column=0, row=4, sticky="W")
        
        # Position values e.g.(x,y)
		self.posVal = Tkinter.Label(statusFrame, text="(x,y)")
		self.posVal.grid(column=1, row=4, sticky="E", padx=2)
        
        # State of Resident (Text)
		stateText = Tkinter.Label(statusFrame, text="State : ")
		stateText.grid(column=0, row=5, sticky="W")

		# State of Resident (Subscribed state)
		self.stateResident = Tkinter.Label(statusFrame, fg="red")
		self.stateResident.grid(column=1, row=5, sticky="E", padx=2)

		#====End of statusFrame====#
		
		#====Start of timeFrame====#
        
		# Parent Frame
		timeFrame = Tkinter.Frame(self, bd=2, relief="groove", width=285, height=50)
		timeFrame.grid(column=0, row=3, padx=5, pady=2.5)
		timeFrame.grid_propagate(False)
		
		# Text that outputs header "Time"
		timeText = Tkinter.Label(timeFrame, text="Time", font=(18), anchor="center")
		timeText.grid(column=0, row=0, sticky="W")
        
		# Text that displays "Current Time"
		currentTimeText = Tkinter.Label(timeFrame, text="Current Time : ")
		currentTimeText.grid(column=0, row=1)
        
		# Text that displays simulation time
		currentTime = Tkinter.Label(timeFrame, text="11:08PM, 27 August 2014")
		currentTime.grid(column=1, row=1, sticky="E", padx=5)

		#====End of timeFrame====#

		#====Start of infoFrame====#

		# Parent frame
		infoFrame = Tkinter.Frame(self, bd=2, relief="groove", width=285, height=90)
		infoFrame.grid(column=0, row=4, padx=5, pady=2.5)
		infoFrame.grid_propagate(False)

		# Text that outputs header "Time"
		infoText = Tkinter.Label(infoFrame, text="Information", font=(18), anchor="w")
		infoText.grid(column=0, row=0, sticky="W")

		# Information display
		genderText = Tkinter.Label(infoFrame, text="Gender : M")
		genderText.grid(column=0, row=1, sticky="W")

		ageText = Tkinter.Label(infoFrame, text="Age :      21")
		ageText.grid(column=0, row=2, sticky="W")

		dobText = Tkinter.Label(infoFrame, text="D.O.B :   07/09/1993")
		dobText.grid(column=0, row=3, sticky="W")
		'''
		genderValue = Tkinter.Label(infoFrame, text="M", anchor="e")
		genderValue.grid(column=1, row=1)

		ageValue = Tkinter.Label(infoFrame, text="21", anchor="e")
		ageValue.grid(column=1, row=2)

		dobValue = Tkinter.Label(infoFrame, text="07/09/1993", anchor="e")
		dobValue.grid(column=1, row=3)
		'''

		#====End of infoFrame====#
	def setupNode(self):
		rospy.init_node('listener', anonymous=True)
		if subscriber is None:
			rospy.Subscriber("python/gui", String, self.residentStatusCallback)
	
	def residentStatusCallback(self, GUImsg):
		global callbackData
		global dataList
		callbackData = GUImsg.data
		#rospy.loginfo(rospy.get_caller_id()+"I heard %s", GUImsg.data)
		dataList = GUImsg.data.split(" ")
		#print(dataList)
		self.healthFiller.config(width=200*(1-(float(dataList[0])/100)))
		self.hungerFiller.config(width=200*(1-(float(dataList[1])/100)))
		self.boredomFiller.config(width=200*(1-(float(dataList[2])/100)))
		self.stateResident.config(text=dataList[5])
		self.posVal.config(text="x=" + dataList[3] + ", y=" + dataList[4])

	# Function that changes width of the bars
	def decreaseHealth(self, value):
		self.healthFiller.config(width=200*(1-value))
		self.hungerFiller.config(width=200*(1-value))
		self.boredomFiller.config(width=200*(1-value))

# Semi recursive function that updates components in GUI i.e. changes bar
def task():
	global perc
	perc -= 0.05
	if perc > -0.05: # There is no 0 in python...
		app.decreaseHealth(perc)
	app.after(1000,task)  # reschedule event in 1 seconds
	

if __name__ == "__main__":
    # Instantiate class
	app = ros_gui(None)
    # Give a title to window
	app.title('Resident')
	#app.after(1000,task)
	app.mainloop()



