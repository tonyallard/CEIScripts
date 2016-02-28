#!usr/bin/python
#Author: Tony Allard
#Date: 14 May 2014
#Description: A Python script for running experiments on the Colin2 Planner

import timeit
import time
import datetime
from subprocess import *
import os
import re
	
#--globals--
RELAX_HEURISTIC="/home/tony/workspace/colin2-withITC/debug/colin/colin-clp"
#STATE_DB = "/home/tony/workspace/colin2/states/"
#STATE_DB = "./states/"
STATE_DB = "./states-p02-updated/"
RESULTS_STORE = "./results/"

#String delimeters
DOMAIN_DELIM="domain"
GOOD_DELIM="Good"
HVAL_DELIM="State Heuristic Value is:"

#Functions
def runPlanner(domain, problem, results, errFile):	
	#determine state number for record
	#assumes only number in filename defines statenum
	stateNums = re.findall('[-+]?\d+[\.]?\d*', domainFile)
	stateNum = int(stateNums[0])
	start = timeit.default_timer()
	proc = Popen([RELAX_HEURISTIC, "-T", domain, problem], stdout=PIPE, stderr=PIPE)
	#extract h-value from output
	buff = proc.stdout.read()
	err = proc.stderr.read()
	elapsed = timeit.default_timer() - start
	errFile.write(err)
	hValIdx = buff.find(HVAL_DELIM)
	if hValIdx >= 0:
		hValIdx = hValIdx + len(HVAL_DELIM)
		results[stateNum] = float(buff[hValIdx+1:-1])
		if (results[stateNum] is 0 and GOOD_DELIM not in domain) :
			errFile.write("Bad State with zero h-val: %s"%problem)
	else: #if h-value not found there was an error, record for analysis
		errFile.write("!!!Problem with state: " + problem + "!!!\n")
	return elapsed

def processState(domain, problem, results, errFile):
	good = False	
	if GOOD_DELIM in domain:
		good = True
	domain = STATE_DB + domain
	problem = STATE_DB + problem
	time_taken = runPlanner(domain, problem, results[good], errFile)
	return time_taken

def getAverage(results):
	if len(results) > 0:
		return reduce(lambda x, y: x + y, results) / len(results)
	return -1

#Main Func
#format timestamp for files
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
#Open file for storring err
errFileName = RESULTS_STORE + st + "-Errors.txt"
errFile = open(errFileName, "w")

results = {True:{}, False:{}}
count = 0.0
time_taken = 0.0
for fileName in os.listdir(STATE_DB):
	if DOMAIN_DELIM in fileName:
		domainFile = fileName
		problemFile = domainFile[:-11] + ".pddl"
		print "Processing %s"%problemFile
		errFile.write("*******Processing %s*******\n"%problemFile)	
		stateTime = processState(domainFile, problemFile, results, errFile)
		time_taken += stateTime
		print "%s took %fs (%fs total so far)"%(problemFile, stateTime, time_taken)
		#print "Elapsed time thus far %.2fs (%.2fs avg)"%(time_taken, float(time_taken)/count)
		count += 1
		#if (count >= 10):
			#break

#close errFile
errFile.close()

#open plot file
dataFileName = RESULTS_STORE + st + "-DataFile.plt"
f = open(dataFileName, "w")

#Print Results
f.write("#Achieved %i heuristic lookups in %.2fs (%.2fs average)\n"%(count, time_taken, time_taken/float(count)))

#Add good state data
goods = results[True]
for x in sorted(goods.iterkeys()):
	f.write("%d\t%.3f\n"%(x, goods[x]))

#seperate good/bad indexes of data
f.write('\n\n')

#add bad state data
bads = results[False]
for x in sorted(bads.iterkeys()):
	f.write("%d\t%.3f\n"%(x, bads[x]))

#plot with GNUPLOT
os.system('gnuplot --persist -e \'plot \"%s\" i 0 t \"Good States\" w linespoints linecolor rgb \"green\", \"\" i 1 t \"Bad States\" w linespoints linecolor rgb \"red\"\'&'%dataFileName)

#Determine averages
avgGood = getAverage(results[True].values())
avgBad = getAverage(results[False].values())
f.write("#Good states received an average heuristic of %.4f\n"%avgGood)
f.write("#Bad states received an average heuristic of %.4f\n"%avgBad)