#!/usr/bin/python

class Job:

	def __init__(self, plannerName, problemName, itr, plannerCommand, validatorCommand, logFile, planFile):
		self.plannerName = plannerName
		self.problemName = problemName
		self.itr = itr
		self.plannerCommand = plannerCommand
		self.validatorCommand = validatorCommand
		self.logFile = logFile
		self.planFile = planFile