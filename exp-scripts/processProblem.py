#!/usr/bin/python

import sys
import subprocess
from timeit import Timer
from shutil import move


#Variables
PROC_FOLDER="/mnt/data/completed/"
COLIN_LOC="/mnt/data/bin/Colin2-withStatePrinter/"
COLIN_EXEC_LOC="/mnt/data/bin/Colin2-withStatePrinter/debug/colin/colin-clp"
TIMEOUT_CMD="timeout -s SIGXCPU 2h"
MEMLIMIT_CMD="ulimit -Sv 10000000"
LOG_FOLDER="/mnt/data/logs/"
DOMAIN_FILE="/mnt/data/MMCR.pddl"

#Get problem parameters
probFullPath = sys.argv[1]
probFile = probFullPath.rsplit('/', 1)[1]
proc_probFile = PROC_FOLDER+probFile

#Move problem to ensure exclusive access
move(probFullPath, proc_probFile)

#Ouput Logging
logFileName = probFile + ".txt"
logFullQual = LOG_FOLDER + logFileName
log = open(logFullQual, "a")

#Setup experiment
reps=1
stdout = log
stderr = log
parameters = "-Th %s %s"%(DOMAIN_FILE, proc_probFile)
external_command = "(cd %s && %s && %s %s %s)"%(COLIN_LOC, MEMLIMIT_CMD, TIMEOUT_CMD, COLIN_EXEC_LOC, parameters)
call_args = """['%s'], stdout=stdout, stderr=stderr"""%(external_command)

print "Processing %s" %probFile

#Run Experiment
log.write("===Processing %s===\n"%proc_probFile)
log.write("===with Command %s===\n" %external_command)
t = Timer(stmt = """subprocess.call(%s, shell=True)"""%call_args, setup="""import subprocess; stdout=open(\"%s\", 'a'); stderr=stdout"""%logFullQual)
timeTaken = t.timeit(reps)

#Write Time Taken to Log
log.write("\n\n===TIME TAKEN===\n")
log.write("%f seconds\n"%timeTaken)
log.write("===EOF===")
log.close()

