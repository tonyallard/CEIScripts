#!/usr/bin/python
import sys
import pickle
from cStringIO import StringIO
import random
from time import gmtime, strftime

EXIT_PROCESS = "EXIT_PROCESS"
REQUEST_PROBLEM = "REQUEST_PROBLEM"
PROBLEM_QUEUE_SIZE = "PROBLEM_QUEUE_SIZE"
CURRENT_ALLOCATION = "CURRENT_ALLOCATION"
PAUSE_WORKERS = "PAUSE_WORKERS"
RESUME_WORKERS = "RESUME_WORKERS"
RESTRICT_WORKERS = "ENFORCE_RESTRICTED_WORKER_NUMBERS"
UNRESTRICT_WORKERS = "RELAX_WORKER_NUMBER_RESTRICTION"

WORKER_EXECUTING_JOB = "WORKER_EXECUTING_JOB"
WORKER_PAUSED = "WORKER_PAUSED"
WORKER_TERMINATED = "WORKER_TERMINATED"

RESTRICTED_WORKER_NUMBER = 5

SEEDED = False

class Message:
	def __init__(self, _id, message):
		self._id = _id
		self.message = message

def getMessageString(_id, message):
	m = Message(_id, message)
	stream = StringIO() 
	pickle.dump(m, stream)
	messageStr = stream.getvalue()
	stream.close()
	return messageStr

def getMessage(data):
	stream = StringIO(data)
	m = pickle.Unpickler(stream)
	message = m.load()
	return message

def seed():
	global SEEDED
	if not SEEDED:
		random.seed()
		SEEDED = True

def getInstanceID():
	seed()
	return random.randint(0, sys.maxint)

def printMessage(text):
	print "%s: %s"%(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
		text)