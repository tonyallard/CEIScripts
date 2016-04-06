#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the running time of the planner.
#Extracts data to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import re
import AnalysisCommon

TIME_DELIM = "===TIME TAKEN==="
PDDL_CONVERT_TIME_DELIM = "#; Time spent converting PDDL state:"
PDDL_FILE_WRTIE_TIME_DELIM = "#; Time spent printing state to file:"
H_TIME_DELIM = "#; Time spent in heuristic:"

MAX_RUNTIME = 7200
MEM_RUNTIME = 9000

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

def main(args):
	csvFile = open('time-data.csv', 'w')
	errExpFile = open('err-exp.log', 'w')
	expTimeoutFile = open('expTimeout.log', 'w')
	expExceedMemFile = open('expExceedMem.log', 'w')
	csvFile.write("Problem, Cargo, Tightness, Problem Number, Label, Running Time\n")
	
	#path = "/mnt/data/160406-Colin-RPG-logs-repaired/"
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

	results = []

	expErrProblems = []
	totalEvalCount = 0

	includeMemFails = False
	includeCPUFails = False

	if AnalysisCommon.checkArgs("-m", args):
		includeMemFails = True
	if AnalysisCommon.checkArgs("-c", args):
		includeCPUFails = True
	
	for filename in os.listdir(path):

		#Check if this is a problem log
		if not AnalysisCommon.isProblemLog(filename):
			continue

		f = open(path+filename, 'r')
		totalEvalCount += 1

		#Buffer file to iterate over many times
		fileBuffer = AnalysisCommon.bufferFile(f)
		
		#Extract particular properties of file
		cargo, tightness, probNumber, probDesc = AnalysisCommon.extractProblemProperties(filename)
	
		#check problem for memory crash		
		if AnalysisCommon.isOutOfMemory(fileBuffer):
			expExceedMemFile.write("%s\n"%filename)
			if includeMemFails:
				results.append([filename, cargo, tightness, probNumber, probDesc, MEM_RUNTIME])
			else:
				results.append([filename, cargo, tightness, probNumber, probDesc, ""])
			continue
		
		#check problem for timeout
		if AnalysisCommon.isCPUTimeout(fileBuffer):
			expTimeoutFile.write("%s\n"%filename)
			if not includeCPUFails:
				results.append([filename, cargo, tightness, probNumber, probDesc, ""])
				continue
		
		#Pull times spent doing different things
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
			#Add data point
			results.append([filename, cargo, tightness, probNumber, probDesc, runTime])
		else:
			#Keep history of those problems could not find a solution
			expErrProblems.append(filename)
	#Print stats
	print ("%i problems evaluated. Average run time of %.2f seconds (%.2f seconds total)."%(totalEvalCount, avgRunTime, avgRunTime * float(probCount)))
	if len(expErrProblems) > 0:
		print "%i appear to have not completed."%len(expErrProblems)
	print ("Other averages: %.2fs spent in the heuristic, %.2fs on PDDL Conversion, %.2fs on file writing. (%.2fs average if better engineered)."%(avgHRunTime, avgPDDLConvertTime, avgPDDLFileWriteTime, (avgRunTime - avgPDDLConvertTime - avgPDDLFileWriteTime)))
	
	#Write CSV File
	sorted(results, key=lambda x: (x[1], -x[2], x[3]))
	results.sort()
	
	for r in results:
		csvFile.write("%s, %i, %f, %i, %s, %s\n"%(r[0], r[1], r[2], r[3], r[4], r[5]))
	#Write average runtime
	csvFile.write("%i, , , , , %f\n"%(probCount, avgRunTime))
	csvFile.close()

	#Write problems that did not complete the exp
	errExpFile.write("\n".join(expErrProblems))
	errExpFile.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)