# -*- coding: UTF-8 -*-

from copy import deepcopy

import struct

import pickle



"""Class to read and parse a binary file from the DRS4
"""
class DRS4FileReader:
	
	"""Constructor, takes file path/file name as argument
	"""
	def __init__(self, fileName):
		self.fileName = fileName
		
		
		self.channelList = [] #List to be populated by the channels
		self.channelCounter = -1 #Counter to keep track of the current channel.
		#Starts at -1, as it updates first thing in the loop

		self.eventList = [] #List to be populated by all the Event objects


		self.wordSize = 4 #A "word" is 4 bytes
		
		
	def parseFile(self):
		with open(self.fileName, "rb") as fil:
		
			#Word 0 just gives DRS version
			fil.read(self.wordSize)
			#Word 1 no info
			fil.read(self.wordSize)
			#Word 2 contains board serial number
			word = fil.read(self.wordSize)
			#struct.unpack(format, word) returns a tuple of values read from the
			#binary "word", translated by the format. H unsigned int, c char.
			wordTuple = struct.unpack("ccH", word)
			boardSerial = wordTuple[2]
			print("Board serial number:", boardSerial)
			
			#Word 3 is channel header. Always at least one channel, so this is always here.
			#4 chars, last one is channel number
			
			word = struct.unpack("cccc", fil.read(self.wordSize))
			while word[0].decode("UTF-8") == "C": #While the current line starts with C
				
				self.channelCounter += 1
				channelNumber = int(word[3])
				#int() turns it into an int.
				self.channelList.append(Channel(channelNumber)) #Creates new channel object
			
				#Next 1024 words are time bin widths for the channel in question. (in ns)
				#4-byte floating point format
				self.channelList[self.channelCounter].setBinWidths(self.read1024Lines(fil, "f"))		
						
				#Word 1028 is possibly another channel header.
				#Definitely 4 chars. Check if channel header (restart loop)
				word = struct.unpack("cccc", fil.read(self.wordSize))
				#print(word)
			
			
			#We now have all the channels created.
			#So now events start!
			
			#If it's EHDR, we have a new event!
			eventCounter = 1
			while word[0].decode("UTF-8") == "E" and word[1].decode("UTF-8") == "H":
				word = self.parseEvent(fil)
				print("Number of events thus far: ", eventCounter)
				eventCounter += 1
				
			
			#Shifts the times of the channels, so that the absolute times match
			for event in self.eventList:
				event.alignChannelTimes()

	
	"""Helper function to read 1024 "words", and return the values as a list.
	"""
	def read1024Lines(self, fil, fmtString):
		
		valueList = []
		
		for i in range(0, 1024):
			word = fil.read(4)
			wordTuple = struct.unpack(fmtString, word)
			#print(wordTuple)
			valueList.extend(wordTuple)
		
		return valueList


	"""Parses one event, creates and returns a new Event object.
	"""
	def parseEvent(self, fileName):
		#First line after EHDR is event serial number
		serialNumber = struct.unpack("I", fileName.read(4))[0]
		#print("Serial number of event is", serialNumber)
		
		#Time the event occurred. Not used right now. TODO
		
		year = struct.unpack("h", fileName.read(2))[0]
		month = struct.unpack("h", fileName.read(2))[0]
		day = struct.unpack("h", fileName.read(2))[0]
		hour = struct.unpack("h", fileName.read(2))[0]
		minute = struct.unpack("h", fileName.read(2))[0]
		second = struct.unpack("h", fileName.read(2))[0]
		millisecond = struct.unpack("h", fileName.read(2))[0]
		
		#print(year, month, day, hour, minute, second, millisecond)
		
		#Following two is the range centre in mV
		rangeCentre = struct.unpack("h", fileName.read(2))[0] #In millivolts
		
		#Next row is board number, skip that for now
		#First two on next row is T#, and then comes the trigger cell.
		#For now: skip 6 bytes to get to trigger cell
		fileName.read(6)
		
		triggerCell = struct.unpack("H", fileName.read(2))[0]
		
		#print("Trigger cell is", triggerCell)
		
		#Create new event object
		self.eventList.append(Event(serialNumber, rangeCentre, triggerCell))
		
		#Here comes the channels
		#C001 through C004 (possibly), starting with header, then Scaler for the channel,
		#and then 1024 voltages
		
		#Read line of 4, check if starts with C, then last char gives channel number
		word = struct.unpack("cccc", fileName.read(self.wordSize))
		chCounter = 0
		while word[0].decode("UTF-8") == "C": #While the current line starts with C
		
			scaler = struct.unpack("i", fileName.read(self.wordSize)) #TODO (throwing this away right now)
			#print("Scaler is", scaler)
			#Seems to be zero most of the time. Is it even an int?
			#Not used right now, anyway.
			
			#Gets the list of voltages
			#1024 2-byte integers.
			inVoltages = []
			for i in range(0, 1024):
				inVoltages.append(struct.unpack("H", fileName.read(2))[0])
				#H instead of h! Important!!! h short, H unsigned short, which is what we have
			
			#Sets the voltages of the last event in the list (that is, the current event)
			self.eventList[-1].setRawVoltages(self.channelList[chCounter], inVoltages)
			chCounter += 1
			
			
			tmpWord = fileName.read(self.wordSize)
			if len(tmpWord) < 4:
				print("End of file reached")
				return (b'0',b'0',b'0',b'0') #Returns "word" of zeroes
			else:
				#print("Temp word is", tmpWord)
				word = struct.unpack("cccc", tmpWord)
			
		#Here the event is over. Return word, so it can be used outside (needed at the point of call)
		return word
	
	
	
	"""Saves the filereader object using Pickle.
	Contains all the events and such.
	Can be loaded by loading the pickle file with something like
	with open("pickle1.pkl", "rb") as inFile:
		reader = pickle.load(inFile)
	
	Argument: path to save to
	"""
	def saveAsPickle(self, filePath):
		with open(filePath, 'wb') as writeFile:
			pickle.dump(self, writeFile, pickle.HIGHEST_PROTOCOL)
		
	
	"""Saves the data as an ascii file, readable by other programs.
	CSV format, more or less
	
	EVENT
	CHANNEL #
	time,voltage
	time,voltage
	time,voltage
	...
	CHANNEL #
	time,voltage
	...
	EVENT
	
	more or less.
	
	Argument: path to save to
	"""
	def saveAsAscii(self, filePath):
		with open(filePath, "w") as outFile:
			
			for event in self.eventList:
				
				outFile.write("EVENT " + str(event.serialNumber) + "\n")
				
				for channel in event.channelList:
					outFile.write("CHANNEL " + str(channel.number) + "\n")
					
					for i in range(0, len(channel.times)):
						outFile.write(str(channel.times[i]) + "," + str(channel.voltages[i]) + "\n")
			

	


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
		self.times = [0.0]*1024 #List to be populated by the times of an event
		self.voltages = [0]*1024 #List to be populated by the calculated proper voltages
		
	def setBinWidths(self, inWidths):
		self.binWidth = inWidths


class Event:
	
	#time, to be implemented. TODO
	
	"""Constructor. Takes event serial number, range center (in millivolts), trigger cell number (0-1023)
	OR IS IT 1-1024?? TODO
	"""
	def __init__(self, SN, RC, TC):
		self.serialNumber = SN
		self.rangeCenter = RC #In millivolts
		self.triggerCell = TC #Measuring starts in trigger cell. 1024 cells on board.
		#So TC is "Voltage bin 0" in binary file.
		#Need to shift to match with times
		
		self.rawVoltages = [0]*1024 #List of 1024 2-byte integers. 0 is RC-0.5 V, 65535 is RC+0.5V
		
		self.channelList = []
		
		#print("Trigger cell:", TC)
		#print("Range center:", RC)
	
	
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
			currChannel.voltages[index] = self.rangeCenter/1000 - 0.5 + self.rawVoltages[i]/65535.0
			#print(self.rawVoltages[i])
			#Rangecenter given in millivolts
			#rawVoltages have trigger cell at index 0
			#currChannel.voltages has cell 0 at index 0
			
			self.calculateTimes(currChannel, i) #Calculates the times for the cells in the current channel
			
		self.channelList.append(currChannel) #Adds current channel to list of channels for event
		
	""" The times have to be calculated taking the trigger cell into consideration.
	Need to add up bin widths of all cells before the one we calculate the time for.
	"""
	def calculateTimes(self, channel, i):
		j = 0
		#i = 0 for trigger cell
		index = (i + self.triggerCell)%1024 #To get correct list placement of time
		#print("i:", i, ",", "index:", index)
		channel.times[index] = 0.0 #Start value
		#Then add together all the ones before!
		while j < i:
			channel.times[index] += channel.binWidth[(j + self.triggerCell)%1024]
			j += 1
			#Timing starts at trigger cell (?)
			
		#print("Index:",index,",","Time:",channel.times[index])
			
	
	"""Gets the times, starting with the trigger cell at index 0.
	Takes channel number as argument.
	"""
	def getTimesTCStart(self, channelNo):
		return (self.channelList[channelNo].times[self.triggerCell:] + 
				self.channelList[channelNo].times[:self.triggerCell])
		
	"""Gets voltages, with trigger cell as index 0.
	Takes channel number as argument.
	"""
	def getVoltagesTCStart(self, channelNo):
		return (self.channelList[channelNo].voltages[self.triggerCell:] + 
				self.channelList[channelNo].voltages[:self.triggerCell])
	
	
	
	"""Cells have different absolute times in different channels.
	Good idea to align them. Cell 0 is the same always (0.0).
	Aligning using channel 1 as base.
	"""
	def alignChannelTimes(self):
		t1 = self.channelList[0].times[0]
		i = 1
		while i < len(self.channelList):
			dt = t1 - self.channelList[i].times[0]
			#print(dt)
			for j in range(0, 1024):
				self.channelList[i].times[j] += dt
			i += 1
		
