import numpy as np
import matplotlib.pyplot as plt

exec(open("pythontest3.py").read())


x = eventList[5].channelList[1].times

y = eventList[5].channelList[1].voltages

for i in range(0, len(x)):
	print(x[i], y[i])

plt.plot(x,y,'*')

plt.show() #To actually show the plot

x2 = np.linspace(0,1024, len(x))


#OBS! Plotted in a bit of a strange order, as times[0] is generally not the smallest time!
#Trigger cell has smallest time.
#So we're not plotting from left to right here, but rather from just right of trigger cell to just left of trigger cell
#(wrapping around)


for i in range(0, len(eventList)):
	plt.figure(i+1)
	plt.plot(eventList[i].getTimesTCStart(1), eventList[i].getVoltagesTCStart(1), '.')
	plt.xlabel("Time [ns]")
	plt.ylabel("Volts")
	plt.show()
