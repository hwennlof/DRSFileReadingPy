# -*- coding: UTF-8 -*-

from copy import deepcopy


""" Each event has a number of channels, coming from deep copies of 
the channels created at the start of the file reading (as the time bin size is constant
throughout the file)
"""
class Channel:
	
	""" Constructor, takes channel number
	"""
	def __init__(self, no):
		self.number = no
		self.binWidth = [0.0]*1024 #Time bin width, in nanoseconds. Float
		self.voltages = [0]*1024 #List to be populated by the calculated proper voltages
		self.times = [0.0]*1024 #List to be populated by the times of an event
		
	def setBinWidths(self, inWidths):
		self.binWidth = inWidths


class Event:
	
	#time, to be implemented. TODO
	
	def __init__(self, SN, RC, TC):
		self.serialNumber = SN
		self.rangeCenter = RC
		self.triggerCell = TC #Measuring starts in trigger cell. 1024 cells on board.
		#So TC is "Voltage bin 0" in binary file.
		#Need to shift to match with times
		
		self.rawVoltages = [0]*1024 #List of 1024 2-byte integers. 0 is RC-0.5 V, 65535 is RC+0.5V
		
		self.channelList = []
	
	
	"""Sets the raw voltages, from the program handling the binary file.
	Creates deep copy of the provided channel object, and stores it in this
	Event object.
	"""
	def setRawVoltages(self, channel, inVoltages):
		self.rawVoltages = inVoltages
		
		self.calculateVoltages(deepcopy(channel))
	
	"""Calculates the proper voltages, using the raw data as offset from the rangeCenter
	"""
	def calculateVoltages(self, currChannel):
		for i in range(0, len(self.rawVoltages)):
			index = (i + self.triggerCell)%1024 #To get correct list placement of new voltage
			currChannel.voltages[index] = self.rangeCenter	 - 0.5 + self.rawVoltages[index]/65535.0
			#Kan ta minus 0.5V på RC, och sen bara lägga till rawVolt/65535... väl?
			
			self.calculateTimes(currChannel, i) #Calculates the times for the cells in the current channel
			
		self.channelList.append(currChannel) #Adds current channel to list of channels for event
		
	""" The times have to be calculated taking the trigger cell into consideration.
	Need to add up bin widths of all cells before the one we calculate the time for.
	"""
	def calculateTimes(self, channel, i):
		j = 0
		#i = 0 for trigger cell
		index = (i + self.triggerCell)%1024 #To get correct list placement of time
		channel.times[index] = 0.0 #Start value
		#Then add together all the ones before!
		while j < i:
			channel.times[index] += channel.binWidth[(j + self.triggerCell)%1024]
			j += 1
			#Timing starts at trigger cell (?)
			
			
	
	
	
	
	"""Cells have different absolute times in different channels.
	Good idea to align them. Cell 0 is the same always (0.0).
	Aligning using channel 1 as base.
	"""
	def alignChannelTimes(self):
		t1 = self.channelList[0].times[0]
		
