#!/usr/bin/python
import sys
import os
import re
import gzip
from subprocess import *

import AnalysisCommon

ACTION_TIME = "[0-9]+\.[0-9]+\:"
ACTION_INSTANCE = "\([A-Za-z0-9\-_ ]+\)"
ACTION_DURATION = "\[D:[0-9]+\.[0-9]+"
DECIMAL_NUMBER = "[0-9]+\.[0-9]+"

def main (args) :
	
	logPath = args[0]
	problemPath = args[1]
	
	specificProblem = False
	problem = ""
	if len(args) == 3:
		specificProblem = True
		problem = args[2]

	if specificProblem:
		print "Implement Me"
		#validatePlan(logPath, problemPath, problem)
	else:
		dirs = ""
		for root, dirs, files in os.walk(logPath)

		print dir(result.next)
		sys.exit(0)

		for filename in os.listdir(logPath):
			fullQualified = os.path.join(logPath, filename)
			try:
				with gzip.open(fullQualified, 'rb') as f:
				
					buffer = AnalysisCommon.bufferFile(f)
			except IOError:
				continue
			f = open("/tmp/plan.tmp", 'w')
			for line in buffer:
				actionTime = re.findall(ACTION_TIME, line)
				if len(actionTime) != 1:
					raise RuntimeError("Error! Multiple action times found: %s"%actionTime)
				actionInstance = re.findall(ACTION_INSTANCE, line)
				if len(actionInstance) != 1:
					raise RuntimeError("Error! Multiple action instances found: %s"%actionInstance)
				actionDuration = re.findall(ACTION_DURATION, line)
				if len(actionDuration) != 1:
					raise RuntimeError("Error! Multiple action durations found: %s"%actionDuration)
				actionDuration = re.findall(DECIMAL_NUMBER, actionDuration[0])
				f.write("%s%s [%s]"%(actionTime[0], actionInstance[0], actionDuration[0]))
			f.close()





#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])