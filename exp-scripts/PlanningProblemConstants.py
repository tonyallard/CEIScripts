#!/usr/bin/python3
import sys
import pickle
from io import BytesIO
import random
from time import localtime, strftime

EXIT_PROCESS = "EXIT_PROCESS"
REQUEST_PROBLEM = "REQUEST_PROBLEM"
PROBLEM_QUEUE_SIZE = "PROBLEM_QUEUE_SIZE"
CURRENT_ALLOCATION = "CURRENT_ALLOCATION"
PAUSE_WORKERS = "PAUSE_WORKERS"
RESUME_WORKERS = "RESUME_WORKERS"
RESTRICT_WORKERS = "ENFORCE_RESTRICTED_WORKER_NUMBERS"
UNRESTRICT_WORKERS = "RELAX_WORKER_NUMBER_RESTRICTION"
TERMINATE_WORKERS = "TERMINATE_WORKERS"

WORKER_EXECUTING_JOB = "WORKER_EXECUTING_JOB"
WORKER_PAUSED = "WORKER_PAUSED"
WORKER_TERMINATED = "WORKER_TERMINATED"

RESTRICTED_WORKER_NUMBER = 8

SEEDED = False

class Message:
	def __init__(self, _id, hostname, message):
		self._id = _id
		self.hostname = hostname
		self.message = message

def getMessageString(_id, message, hostname = ""):
	m = Message(_id, hostname, message)
	stream = BytesIO()
	pickle.dump(m, stream)
	messageStr = stream.getvalue()
	stream.close()
	return messageStr

def getMessage(data):
	stream = BytesIO(data)
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
	return random.randint(0, sys.maxsize)

def printMessage(text):
	print("%s: %s"%(strftime("%Y-%m-%d %H:%M:%S", localtime()),
		text))
	sys.stdout.flush()