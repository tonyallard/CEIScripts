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
USER_TIME_DELIM = "user "
SYSTEM_TIME_DELIM = "sys "

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

def extractSystemRunTime(logFile):
	for line in logFile:
		if SYSTEM_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple system run times found: %s"%runTime)
			return float(runTime[0])
	return -1

def extractUserRuntime(logFile):
	for line in logFile:
		if USER_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple user run times found: %s"%runTime)
			return float(runTime[0])
	return -1

def extractRunTime(logFile):
	user = extractUserRuntime(logFile)
	sys = extractUserRuntime(logFile)
	if (user == -1) or (sys == -1):
		raise RuntimeError("Error extracting runtime (user: %f, sys: %f)"%(user, sys))
	return user + sys

def main(args):
	
	path = args[0]

	csvFile = open('time-data.csv', 'w')
	csvFile.write("Problem, Running Time,Heuristic Time,PDDL Convert Time,PDDL Write Time\n")
	
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
		fullQialified = os.path.join(path, filename)
		f = open(fullQialified, 'r')
		fileBuffer = AnalysisCommon.bufferFile(f)

		#Check if this is a problem log
		if not AnalysisCommon.isProblemLog(filename, fileBuffer):
			continue

		totalEvalCount += 1

		#check problem for memory crash		
		if not includeMemFails and AnalysisCommon.isOutOfMemory(fileBuffer):
			expErrProblems.append(filename)
			continue
		
		#check problem for timeout
		if not includeCPUFails and AnalysisCommon.isCPUTimeout(fileBuffer):
			expErrProblems.append(filename)
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
			results.append([filename, runTime, hRunTime, pddlConvertTime, pddlFileWriteTime])
		else:
			#Keep history of those problems could not find a solution
			expErrProblems.append(filename)
	#Print stats
	print ("%i problems evaluated. Average run time of %.2f seconds (%.2f seconds total)."%(totalEvalCount, avgRunTime, avgRunTime * float(probCount)))
	if len(expErrProblems) > 0:
		print "%i appear to have not completed."%len(expErrProblems)
	print ("Other averages: %.2fs spent in the heuristic, %.2fs on PDDL Conversion, %.2fs on file writing. (Runtime of %.2fs average if better engineered)."%(avgHRunTime, avgPDDLConvertTime, avgPDDLFileWriteTime, (avgRunTime - avgPDDLConvertTime - avgPDDLFileWriteTime)))
	
	#Write CSV File
	sorted(results, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))
	results.sort()
	
	for r in results:
		csvFile.write("%s,%f,%f,%f,%f\n"%(r[0], r[1], r[2], r[3], r[4]))
	#Write average runtime
	csvFile.write("%i,%f,%f,%f,%f\n"%(probCount, avgRunTime, avgHRunTime, avgPDDLConvertTime, avgPDDLFileWriteTime))
	csvFile.close()

	#Write problems that did not complete the exp
	if len(expErrProblems):
		errExpFile = open('error-problems.log', 'w')
		errExpFile.write("\n".join(expErrProblems))
		errExpFile.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])