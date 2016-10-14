#!/usr/bin/python

import os
import sys
import subprocess
import socket
import time
from timeit import Timer
from shutil import move
from random import randint
from time import sleep

#Variables
PROC_FOLDER="/mnt/data/completed/"
COLIN_LOC="/mnt/data/bin/Colin2-withStatePrinter/"
COLIN_EXEC_LOC="/mnt/data/bin/Colin2-withStatePrinter/debug/colin/colin-clp"
TIMEOUT_CMD="timeout -s SIGXCPU 2h"
TIME_CMD = "time -p"
MEMLIMIT_CMD="ulimit -Sv 2000000"
LOG_FOLDER="/mnt/data/logs/"
DOMAIN_FILE="/mnt/data/MMCR.pddl"
# DOMAIN_FILE="/mnt/data/SAT-DOMAIN.PDDL"
# DOMAIN_FILE="/mnt/data/PIPES-DOMAIN.PDDL"

def main(args, n=30):
	#Get problem parameters
	probFullPath = args[0]
	probFile = probFullPath.rsplit('/', 1)[1]
	proc_probFile = PROC_FOLDER+probFile

	#Wait random timeout to avoid duplicates
	sleepTime = randint(10,150)
	print "Sleeping for %is\n"%sleepTime
	sleep(sleepTime)
	#Move problem to ensure exclusive access
	try:
		move(probFullPath, proc_probFile)
	except IOError:
		print "Another Process has %s"%probFile
		return

	print "Processing %s on %s" %(probFile, socket.gethostname())

	for itr in range(0, n):
		#Ouput Logging
		bufsize = 0
		logFileName = "%s-%i.txt"%(probFile, itr)
		logFullQual = os.path.join(LOG_FOLDER, logFileName)
		log = open(logFullQual, "a", bufsize)

		#Setup experiment
		reps=1
		stdout = log
		stderr = log
		#Colin-TRH
		#parameters = "-h -b -v1 %s %s"%(DOMAIN_FILE, proc_probFile)
		#Colin-RPG
		parameters = "-3 -v1 %s %s"%(DOMAIN_FILE, proc_probFile)
		external_command = "(cd %s && %s && %s %s %s %s)"%(COLIN_LOC, MEMLIMIT_CMD, TIMEOUT_CMD, TIME_CMD, COLIN_EXEC_LOC, parameters)
		call_args = """['%s'], stdout=stdout, stderr=stderr"""%(external_command)

		#Run Experiment
		log.write("===%s: Processing %s on %s===\n"%(time.strftime("%d %m %Y - %H:%M:%S"), proc_probFile, socket.gethostname()))
		log.write("===with Command %s===\n" %external_command)
		t = Timer(stmt = """subprocess.call(%s, shell=True)"""%call_args, setup="""import subprocess; stdout=open(\"%s\", 'a'); stderr=stdout"""%logFullQual)
		timeTaken = t.timeit(reps)

		#Write Time Taken to Log
		log.write("\n\n===TIME TAKEN===\n")
		log.write("%f seconds\n"%timeTaken)
		log.write("===EOF===")
		log.close()

#Run Main Function
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Error: There must be 2 arguments. Received %i"%len(sys.argv)
		print sys.argv
		sys.exit(1)
	main(sys.argv[1:])