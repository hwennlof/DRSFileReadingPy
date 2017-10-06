
from pyDRSread import *

import struct

FILENAME = "171006_test1_10Samples.dat"


channelList = [] #List to be populated by the channels
channelCounter = 0 #Counter to keep track of the current channel

eventList = [] #List to be populated by all the Event objects


wordSize = 4 #A "word" is 4 bytes


"""Helper function to read 1024 "words", and return the values as a list.
"""
def read1024Lines(fil, fmtString):
	
	valueList = []
	
	for i in range(0, 1024):
		word = fil.read(4)
		wordTuple = struct.unpack(fmtString, word)
		print(wordTuple)
		valueList.extend(wordTuple)
	
	return valueList


"""Parses one event, creates and returns a new Event object.
"""
def parseEvent(fileName):
	#First line after EHDR is event serial number
	serialNumber = struct.unpack("I", fileName.read(4))[0]
	#print("Serial number of event is", serialNumber)
	
	#For now we throw away next 3.5 words (14 bytes)
	#It's actually the time the event occurred. TODO
	fileName.read(14)
	#Following two is the range centre in mV
	rangeCentre = struct.unpack("h", fileName.read(2))[0] #In millivolts
	
	#print("Range center is", rangeCentre)
	
	#Next row is board number, skip that for now
	#First two on next row is T#, and then comes the trigger cell.
	#For now: skip 6 bytes to get to trigger cell
	fileName.read(6)
	
	triggerCell = struct.unpack("h", fileName.read(2))[0]
	
	#print("Trigger cell is", triggerCell)
	
	#Create new event object
	eventList.append(Event(serialNumber, rangeCentre, triggerCell))
	
	#Here comes the channels
	#C001 through C004 (possibly), starting with header, then Scaler for the channel,
	#and then 1024 voltages
	
	#Read line of 4, check if starts with C, then last char gives channel number
	word = struct.unpack("cccc", fil.read(wordSize))
	chCounter = 0
	while word[0].decode("UTF-8") == "C": #While the current line starts with C
		#print(word, fil.tell())
		#First line is scaler, in Hz
		#Not sure what that means right now.
		scaler = struct.unpack("i", fil.read(wordSize)) #TODO (throwing this away right now)
		#print("Scaler is", scaler)
		#Seems to be zero mst of the time. Is it even an int?
		#Not used right now, anyway.
		
		#Gets the list of voltages
		#1024 2-byte integers.
		inVoltages = []
		for i in range(0, 1024):
			inVoltages.append(struct.unpack("H", fil.read(2))[0])
			#H instead of h! Important!!! h short, H unsigned short, which is what we have
		
		#print(inVoltages)
		#Sets the voltages of the last event in the list (that is, the current event)
		eventList[-1].setRawVoltages(channelList[chCounter], inVoltages)
		chCounter += 1
		
		
		tmpWord = fil.read(wordSize)
		if len(tmpWord) < 4:
			print("End of file reached")
			return (b'0',b'0',b'0',b'0') #Returns "word" of zeroes
		else:
			#print("Temp word is", tmpWord)
			word = struct.unpack("cccc", tmpWord)
		
	#Here the event is over. Return word, so it can be used outside (needed at the point of call)
	return word
	


with open(FILENAME, "rb") as fil:
	
	#Word 0 just gives DRS version
	fil.read(wordSize)
	#Word 1 no info
	fil.read(wordSize)
	#Word 2 contains board serial number
	word = fil.read(wordSize)
	#struct.unpack(format, word) returns a tuple of values read from the
	#binary "word", translated by the format. H unsigned int, c char.
	wordTuple = struct.unpack("ccH", word)
	boardSerial = wordTuple[2]
	print(boardSerial)
	
	#Word 3 is channel header. Always at least one channel, so this is always here.
	#4 chars, last one is channel number
	channelNumber = int(struct.unpack("cccc", fil.read(wordSize))[3])
	#print("Channel number is", channelNumber)
	#int() turns it into an int.
	channelList.append(Channel(channelNumber)) #Creates new channel object
	
	#Next 1024 words are time bin widths for the channel in question. (in ns)
	#4-byte floating point format
	channelList[channelCounter].setBinWidths(read1024Lines(fil, "f"))
	
	#print(channelList[channelCounter].binWidth)
	
	#Word 1028 is possibly another channel header.
	#Definitely 4 chars. Check if channel header.
	word = struct.unpack("cccc", fil.read(wordSize))
	if word[0].decode("UTF-8") == "C": #decode() needed to convert from "byte char" to char
		#print("We have another channel!")
		channelCounter += 1 #Increase the channel counter
		#Want to do the whole channel thing again
		channelNumber = int(word[3])
		channelList.append(Channel(channelNumber)) #Creates new channel object
		channelList[channelCounter].setBinWidths(read1024Lines(fil, "f"))
		#print(channelList[channelCounter].binWidth)
	
	#Might be another channel. I should really make a loop for this. TODO
	word = struct.unpack("cccc", fil.read(wordSize))
	if word[0].decode("UTF-8") == "C": #decode() needed to convert from "byte char" to char
		#print("We have another channel!")
		channelCounter += 1 #Increase the channel counter
		#Want to do the whole channel thing again
		channelNumber = int(word[3])
		channelList.append(Channel(channelNumber)) #Creates new channel object
		channelList[channelCounter].setBinWidths(read1024Lines(fil, "f"))
		#print(channelList[channelCounter].binWidth)
	else:
		print(word)
	
	
	#If it's EHDR, we have a new event!
	eventCounter = 1
	while word[0].decode("UTF-8") == "E" and word[1].decode("UTF-8") == "H":
		word = parseEvent(fil)
		print("Number of events thus far: ", eventCounter)
		eventCounter += 1
		
		
		
	
	#Shifts the times of the channels, so that the absolute times match
	for event in eventList:
		event.alignChannelTimes()



"""Helper function to skip a line in the file
"""
def skipLine(fil, wordLength):
	fil.read(wordLength)
	
