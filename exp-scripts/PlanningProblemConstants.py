#!/usr/bin/python
import sys
import pickle
from cStringIO import StringIO
import random

EXIT_PROCESS = "EXIT_PROCESS"
REQUEST_PROBLEM = "REQUEST_PROBLEM"
PROBLEM_QUEUE_SIZE = "PROBLEM_QUEUE_SIZE"
CURRENT_ALLOCATION = "CURRENT_ALLOCATION"
WORKER_TERMINATED = "WORKER_TERMINATED"
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