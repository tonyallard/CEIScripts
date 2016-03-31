#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the running time of the planner.
#Extracts states evaluated to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import re

TIME_DELIM = "===TIME TAKEN==="

def extractRunTime(logFile):
	for line in logFile:
		if TIME_DELIM in line:
			line = next(logFile)
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%runTime)
			return float(runTime[0])
	return -1

def main(args):
	csvFile = open('time-data.csv', 'w')
	errExpFile = open('err-exp.log', 'w')
	csvFile.write("Problem, Running Time\n")
	path = "/mnt/data/logs/"
	avgRunTime = 0
	probCount = 0
	errProblems = []
	for filename in os.listdir(path):
		f = open(path+filename, 'r')
		runTime = extractRunTime(f)
		if runTime != -1:
			probCount += 1
			avgRunTime = (avgRunTime * ((probCount - 1) / float(probCount))) + (runTime / float(probCount))
			csvFile.write("%s, %f\n"%(filename, runTime))
		else:
			errProblems.append(filename)
	print ("%i problems evaluated. Average run time of %f seconds (%f seconds total). %i were not completed."%(probCount, avgRunTime, avgRunTime * float(probCount), len(errProblems)))
	csvFile.write("%i, %f\n"%(probCount, avgRunTime))
	csvFile.close()
	errExpFile.write("\n".join(errProblems))
	errExpFile.close()
	#print "These problems did not complete their experiments: \n-%s"%"\n- ".join(errProblems)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)