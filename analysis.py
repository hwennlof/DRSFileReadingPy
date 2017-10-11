import pickle
import matplotlib.pyplot as plt


#Run datatreatment.py first to get Pickle files to analyse!

FILENAME = "./TreatedData/171006_test1_10Samples.pkl"



with open(FILENAME, "rb") as inFile:
	reader = pickle.load(inFile)


eventList = reader.eventList

for i in range(0, len(eventList)):
	plt.figure(i+1)
	#plt.plot(eventList[i].getTimesTCStart(1), eventList[i].getVoltagesTCStart(1), '.')
	chNo = 0
	#plt.plot(eventList[i].channelList[chNo].times, eventList[i].channelList[chNo].voltages)
	plt.plot(eventList[i].getTimesTCStart(chNo), eventList[i].getVoltagesTCStart(chNo), '-')
	chNo = 1
	#plt.plot(eventList[i].channelList[chNo].times, eventList[i].channelList[chNo].voltages,'r')
	plt.plot(eventList[i].getTimesTCStart(chNo), eventList[i].getVoltagesTCStart(chNo), '-r')
	
	plt.xlabel("Time [ns]")
	plt.ylabel("Volts")
	plt.show()
