#!/usr/bin/python

class Job:

	def __init__(self, problemName, itr, plannerCommand, validatorCommand, logFile, planFile):
		self.problemName = problemName
		self.itr = itr
		self.plannerCommand = plannerCommand
		self.validatorCommand = validatorCommand
		self.logFile = logFile
		self.planFile = planFile