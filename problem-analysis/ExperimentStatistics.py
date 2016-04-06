#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Generates a Bunch of Stats From the Experiment
import sys
import os
import re
import AnalysisCommon

#LOG_PATH = "/mnt/data/160406-Colin-RPG-logs-repaired/"
LOG_PATH = "/mnt/data/160404-Colin-TRH-logs/"
PROB_PATH = "/mnt/data/completed"

SOLVED = 1
UNSOLVEABLE = 2
EXCEEDED_MEM_LIMIT = 3
EXCEEDED_CPU_TIME_LIMIT = 4
ERROR_OTHER = 5

def checkLogsExist():
	errProblems = []

	for problem in os.listdir(PROB_PATH):
		if AnalysisCommon.isProblemFile(problem):
			logExisits = False
			for log in os.listdir(LOG_PATH):
				if AnalysisCommon.isProblemLog(log):
					if problem in log:
						logExisits = True
			if not logExisits:
				errProblems.append(problem)

	#Print err problems
	if len(errProblems) > 0:
		print "ERROR: There following problems have no log file:"
		for prob in errProblems:
			print prob
	else:
		print "Looks like all logs have been generated."

def incrementValue(aMap, key, key2):
	if key not in aMap:
		aMap[key] = {}
		aMap[key][SOLVED] = 0
		aMap[key][UNSOLVEABLE] = 0
		aMap[key][EXCEEDED_MEM_LIMIT] = 0
		aMap[key][EXCEEDED_CPU_TIME_LIMIT] = 0
		aMap[key][ERROR_OTHER] = 0

	aMap[key][key2] += 1

def main(args):
	
	checkLogsExist()

	totalEval = 0
	totalSuccess = 0
	unsolveable = 0
	exceedMemory = 0
	exceedCPULimit = 0
	errorOther = 0

	probsUnsolveable = []
	probsExceedMem = []
	probsExceedCPU = []
	probsErrOther = []

	cargoCount = {}
	tighnessCount = {}

	for logFile in os.listdir(LOG_PATH):
		#Check if this is a problem log
		if not AnalysisCommon.isProblemLog(logFile):
			continue

		#Extract particular properties of file
		cargo, tightness, probNumber, probDesc = AnalysisCommon.extractProblemProperties(logFile)
		
		log = open(LOG_PATH+logFile, 'r')
		logBuffer = AnalysisCommon.bufferFile(log)
		totalEval += 1
		
		#Check how the problem went
		if AnalysisCommon.isSuccessful(logBuffer):
			totalSuccess += 1
			incrementValue(cargoCount, cargo, SOLVED)
			incrementValue(tighnessCount, tightness, SOLVED)
		elif AnalysisCommon.isUnsolveable(logBuffer):
			probsUnsolveable.append(logFile[:-4])
			unsolveable += 1
			incrementValue(cargoCount, cargo, UNSOLVEABLE)
			incrementValue(tighnessCount, tightness, UNSOLVEABLE)
		elif AnalysisCommon.isOutOfMemory(logBuffer):
			probsExceedMem.append(logFile[:-4])
			exceedMemory += 1
			incrementValue(cargoCount, cargo, EXCEEDED_MEM_LIMIT)
			incrementValue(tighnessCount, tightness, EXCEEDED_MEM_LIMIT)
		elif AnalysisCommon.isCPUTimeout(logBuffer):
			probsExceedCPU.append(logFile[:-4])
			exceedCPULimit += 1
			incrementValue(cargoCount, cargo, EXCEEDED_CPU_TIME_LIMIT)
			incrementValue(tighnessCount, tightness, EXCEEDED_CPU_TIME_LIMIT)
		else:
			probsErrOther.append(logFile[:-4])
			errorOther += 1
			incrementValue(cargoCount, cargo, ERROR_OTHER)
			incrementValue(tighnessCount, tightness, ERROR_OTHER)

	print "===STATS==="
	totalFail = exceedMemory+exceedCPULimit+errorOther
	print "%i problems evaluated."%totalEval
	print "%i found solutions (%.2f%%), and %i failed (%.2f%%). Sanity check: %i problems"%(totalSuccess, totalSuccess/float(totalEval)*100, totalFail, totalFail/float(totalEval)*100, totalSuccess+totalFail)
	print #
	print "%i were unsolveable (%.2f%%)"%(unsolveable, unsolveable/float(totalEval)*100)
	print "%i exceeded 10GB memory (%.2f%%)"%(exceedMemory, exceedMemory/float(totalEval)*100)
	print "%i exceeded 2hr CPU time limit (%.2f%%)"%(exceedCPULimit, exceedCPULimit/float(totalEval)*100)
	print "%i failed in some other weird and wonderful way (%.2f%%)"%(errorOther, errorOther/float(totalEval)*100)

	
	if (AnalysisCommon.checkArgs("-u", args)):
		print #Break it up

		print "===Problems that were Unsolveable:"
		for prob in probsUnsolveable:
			print prob

	if (AnalysisCommon.checkArgs("-m", args)):
		print #Break it up

		print "===Problems exceeding memory limit:"
		for prob in probsExceedMem:
			print prob

	if (AnalysisCommon.checkArgs("-c", args)):
		print #Break it up

		print "===Problems exceeding CPU time limit:"
		for prob in probsExceedCPU:
			print prob

	if (AnalysisCommon.checkArgs("-o", args)):
		print #Break it up

		print "===Problems failing in other ways:"
		for prob in probsErrOther:
			print prob

	if (AnalysisCommon.checkArgs("-b", args)):
		print #Break it up

		print "===Solution Breakdown:"
		print #Break it up

		print "Cargo:"
		print "Num Cargo, Solved, Unsolveable, Exceed Memory Limit, Exceeded CPU Timeout, Error Other"
		for c in cargoCount:
			print "%i, %i, %i, %i, %i, %i"%(c, cargoCount[c][SOLVED], cargoCount[c][UNSOLVEABLE], cargoCount[c][EXCEEDED_MEM_LIMIT], cargoCount[c][EXCEEDED_CPU_TIME_LIMIT], cargoCount[c][ERROR_OTHER])

		print #Break it up

		print "Tightness:"
		print "Tightness, Solved, Unsolveable, Exceed Memory Limit, Exceeded CPU Timeout, Error Other"
		for t in tighnessCount:
			print "%f, %i, %i, %i, %i, %i"%(t, tighnessCount[t][SOLVED], tighnessCount[t][UNSOLVEABLE], tighnessCount[t][EXCEEDED_MEM_LIMIT], tighnessCount[t][EXCEEDED_CPU_TIME_LIMIT], tighnessCount[t][ERROR_OTHER])

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)