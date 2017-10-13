
from pyDRSread import *

"""Converts data file from DRS4 to a pickled object containing
all the events,
and to an ascii file containing all the events and time-voltage pairs.
"""


DATAFILENAME = "171006_test1_10Samples.dat"

SAVEFILENAME = "./TreatedData/" + DATAFILENAME.split(".")[0] #Same as data file name, just remove the file ending
#SAVEFILENAME = ""

fileReader = DRS4FileReader(DATAFILENAME)	

fileReader.parseFile() #Parses the datafile.
#All data ssaved in the fileReader object


fileReader.saveAsPickle(SAVEFILENAME + ".pkl")
fileReader.saveAsAscii(SAVEFILENAME + ".csv")


