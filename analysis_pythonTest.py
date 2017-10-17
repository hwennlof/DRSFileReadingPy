import pickle
import matplotlib.pyplot as plt
import numpy as np
#import ROOT
#Can't get ROOT to work for importing on this computer, it seems...

import scipy.optimize as sciOp

import bisect



#Run datatreatment.py first to get Pickle files to analyse!

FILENAME = "./TreatedData/171006_test1_10Samples.pkl"



with open(FILENAME, "rb") as inFile:
	reader = pickle.load(inFile)


eventList = reader.eventList



"""Function to find indexes of list, closest to the given
x-values, to be able to use times rather than indices when deciding region.
Returns index with time closest to the given minTime and maxTime.
"""
def timeToIndex(timeVector, minTime, maxTime):
	minIndex = bisect.bisect_left(timeVector, minTime)
	maxIndex = bisect.bisect_right(timeVector, maxTime)
	return minIndex, maxIndex
	

"""Function to use for the curve fit.
takes x as argument, and all the parameters.
"""
def expFit(x, a, b, c):
	return a + b*np.exp(c*x)
	#a + b*e^(c*x)


def gaussianFit(x, c, ampl, centre, width):
	return c + ampl*np.exp(-0.5*((x - centre)/width)**2)
	#OBS Python uses ** for ^


def gaussBgFit(x, t0, c, ampl, centre, width):
	
	def helper(xval):
		if xval <= t0:
			return c
		else:
			return c + ampl*np.exp(-0.5*((xval - centre)/width)**2)
			#OBS Python uses ** for ^
	
	y = np.zeros(x.shape)
	for i in range(0, len(y)):
		y[i] = helper(x[i])
	
	return y



def gaussBgMFit(x, t0, c, m, ampl, centre, width):
	
	def helper(xval):
		if xval <= t0:
			return c + m*(xval-t0)
		else:
			return c + m*(xval-t0) + ampl*np.exp(-0.5*((xval - centre)/width)**2)
			#OBS Python uses ** for ^
	
	y = np.zeros(x.shape)
	for i in range(0, len(y)):
		y[i] = helper(x[i])
	
	return y
	

def correctFit(x, t0, a, m, b, c):
	
	def helper(xval):		
		if xval <= t0:
			return a + m*(xval - t0)
		else:
			return a + m*(xval - t0) - b*(np.exp(-((xval-t0)/c)) - 1)
	
	y = np.zeros(x.shape)
	for i in range(0, len(y)):
		y[i] = helper(x[i])
	
	return y


plt.figure(1)
chNo = 0

plt.xlabel("Time [ns]")
plt.ylabel("Volts")


x1 = eventList[0].getTimesTCStart(chNo)
y1 = eventList[0].getVoltagesTCStart(chNo)

y1 = [y*100 for y in y1] #Multiplies by factor, for better fits...

#y1 = [y*1000 for y in y1]

#plt.plot(x1, y1, '.')


#Variable pointing to the function we'll use for the fit
fitFunc = correctFit

fitTimeMin = 0
fitTimeMax = 750

fitMinBin, fitMaxBin = timeToIndex(eventList[0].getTimesTCStart(chNo), fitTimeMin, fitTimeMax)

startGuess = [600, 0.1, 1, 10, 1] #1,1,1 in default. Something is needed. To get correct scale, if nothing else
popt, pcov = sciOp.curve_fit(fitFunc, x1[fitMinBin:fitMaxBin], y1[fitMinBin:fitMaxBin], startGuess)



#startGuess = [0, 0.1, 600, 100] #1,1,1 in default. Something is needed. To get correct scale, if nothing else
#popt, pcov = sciOp.curve_fit(gaussianFit, x1[fitMinBin:fitMaxBin], y1[fitMinBin:fitMaxBin], startGuess)
#curve_fit returns optimal parameters for fit, and estimated covariance.
#https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
#Works if a decent guess is given...


print(popt)

plt.plot(x1, y1,'.')

x2 = np.linspace(x1[fitMinBin], x1[fitMaxBin], 1000) #Just used for plotting fitted curve
y2 = fitFunc(x2, *popt)

plt.plot(x2, y2, 'g')

plt.show()

#for i in range(0, len(eventList)):
	#plt.figure(i+1)
	##plt.plot(eventList[i].getTimesTCStart(1), eventList[i].getVoltagesTCStart(1), '.')
	#chNo = 0
	##plt.plot(eventList[i].channelList[chNo].times, eventList[i].channelList[chNo].voltages)
	#plt.plot(eventList[i].getTimesTCStart(chNo), eventList[i].getVoltagesTCStart(chNo), '-')
	#chNo = 1
	##plt.plot(eventList[i].channelList[chNo].times, eventList[i].channelList[chNo].voltages,'r')
	#plt.plot(eventList[i].getTimesTCStart(chNo), eventList[i].getVoltagesTCStart(chNo), '-r')
	
	#plt.xlabel("Time [ns]")
	#plt.ylabel("Volts")
	#plt.show()
