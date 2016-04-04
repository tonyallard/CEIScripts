#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the EHC Guidance Histogram from log files.
#Extracts data to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import re

EHC_DELIM = "#; EHC Performance Histogram:"
DEPTH_DELIM = "#; "

def extractEHCDepths(logFile):
	histogram = {}
	for line in logFile:
		if EHC_DELIM in line:
			line = next(logFile)
			while DEPTH_DELIM in line:
				values = re.findall(r'\d+', line)
				if len(values) != 2:
					raise RuntimeError("Error! Multiple values found: %s"%runTime)
				histogram[int(values[0])] = int(values[1])
				line = next(logFile)
	return histogram

def main(args):
	csvFile = open('ehc-data.csv', 'w')
	csvFile.write("Depth, Count\n")
	histogram = {}
	path = "/mnt/data/160404-Colin-TRH-logs/"
	avgDepth = 0
	probCount = 0
	for filename in os.listdir(path):
		f = open(path+filename, 'r')
		hist = extractEHCDepths(f)
		if len(hist) > 0:
			probCount += 1
			for x in hist:
				if x in histogram:
					histogram[x] += hist[x]
				else:
					histogram[x] = hist[x]


	#Save histogram to file
	for x in histogram:
		csvFile.write("%i, %i\n"%(x, histogram[x]))
		avgDepth += histogram[x]
	avgDepth /= float(probCount)
	print ("%i problems evaluated. Average EHC Depth of %f."%(probCount, avgDepth))
	csvFile.write("%i, %f\n"%(probCount, avgDepth))
	csvFile.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)