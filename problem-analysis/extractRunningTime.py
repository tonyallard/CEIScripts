#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the running time of the planner.
#Extracts data to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import re

TIME_DELIM = "===TIME TAKEN==="
PDDL_CONVERT_TIME_DELIM = "#; Time spent converting PDDL state:"
PDDL_FILE_WRTIE_TIME_DELIM = "#; Time spent printing state to file:"
H_TIME_DELIM = "#; Time spent in heuristic:"

TIMEOUT_DELIM = "timeout: the monitored command dumped core"

def extractPDDLFileWriteTime(logFile):
	for line in logFile:
		if PDDL_FILE_WRTIE_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple PDDL file write times found: %s"%runTime)
			return float(runTime[0])
	return -1

def extractPDDLConvertTime(logFile):
	for line in logFile:
		if PDDL_CONVERT_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple PDDL conversion times found: %s"%runTime)
			return float(runTime[0])
	return -1

def extractHRunTime(logFile):
	for line in logFile:
		if H_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple heuristic run times found: %s"%runTime)
			return float(runTime[0])
	return -1

def extractRunTime(logFile):
	logItr = iter(logFile)
	for line in logItr:
		if TIME_DELIM in line:
			line = next(logItr)
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple run times found: %s"%runTime)
			return float(runTime[0])
	return -1

def hasTimedOut(logFile):
	for line in logFile:
		if TIMEOUT_DELIM in line:
			return True
	return False

def main(args):
	csvFile = open('time-data.csv', 'w')
	errExpFile = open('err-exp.log', 'w')
	csvFile.write("Problem, Cargo, Tightness, Label, Running Time\n")
	path = "/mnt/data/160404-Colin-TRH-logs/"
	
	#Averages
	avgRunTime = 0.0
	avgHRunTime = 0.0
	avgPDDLConvertTime = 0.0
	avgPDDLFileWriteTime = 0.0

	#Prob Counts
	probCount = 0
	avgHRunTimeCount = 0
	avgPDDLConvertTimeCount = 0
	avgPDDLFileWriteTimeCount = 0

	errProblems = []
	for filename in os.listdir(path):
		cargo = filename[12:13]
		tightness = "%s.%s"%(filename[14:15], filename[16:filename.rfind("-")])
		probDesc = "%s:%s"%(cargo, tightness)
		f = open(path+filename, 'r')
		fileBuffer = []
		for line in f:
			fileBuffer.append(line)
		
		if hasTimedOut(fileBuffer):
			continue
		
		runTime = extractRunTime(fileBuffer)
		if runTime != -1:
			probCount += 1
			hRunTime = extractHRunTime(fileBuffer)
			pddlConvertTime = extractPDDLConvertTime(fileBuffer)
			pddlFileWriteTime = extractPDDLFileWriteTime(fileBuffer)
			avgRunTime = (avgRunTime * ((probCount - 1) / float(probCount))) + (runTime / float(probCount))
			
			if hRunTime != -1:
				avgHRunTimeCount += 1
				avgHRunTime = (avgHRunTime * ((avgHRunTimeCount - 1) / float(avgHRunTimeCount))) + (hRunTime / float(avgHRunTimeCount))
			if pddlConvertTime != -1:
				avgPDDLConvertTimeCount += 1
				avgPDDLConvertTime = (avgPDDLConvertTime * ((avgPDDLConvertTimeCount - 1) / float(avgPDDLConvertTimeCount))) + (pddlConvertTime / float(avgPDDLConvertTimeCount))	
			if pddlFileWriteTime != -1:
				avgPDDLFileWriteTimeCount += 1
				avgPDDLFileWriteTime = (avgPDDLFileWriteTime * ((avgPDDLFileWriteTimeCount - 1) / float(avgPDDLFileWriteTimeCount))) + (pddlFileWriteTime / float(avgPDDLFileWriteTimeCount))
			csvFile.write("%s, %s, %s, %s, %f\n"%(filename, cargo, tightness, probDesc, runTime))
		else:
			errProblems.append(filename)
	print ("%i problems evaluated. Average run time of %f seconds (%f seconds total). %i were not completed."%(probCount, avgRunTime, avgRunTime * float(probCount), len(errProblems)))
	print ("Other averages: %fs spent in the heuristic, %fs on PDDL Conversion, %fs on file writing. (%fs average if better engineered)."%(avgHRunTime, avgPDDLConvertTime, avgPDDLFileWriteTime, (avgRunTime - avgPDDLConvertTime - avgPDDLFileWriteTime)))
	csvFile.write("%i, , , , %f\n"%(probCount, avgRunTime))
	csvFile.close()
	errExpFile.write("\n".join(errProblems))
	errExpFile.close()
	#print "These problems did not complete their experiments: \n-%s"%"\n- ".join(errProblems)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)