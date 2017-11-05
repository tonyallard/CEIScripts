#!/usr/bin/python

import ExtractSuccess
import ExtractRunningTime
import ExtractStatesEval
import ExtractDeadEnds

class ProblemDomainStats:

	SUCCESS_IDX = 0
	COMP_TIME_IDX = 1
	H_TIME_IDX = 2
	STATES_EVAL_IDX = 3
	H_STATES_EVAL_IDX = 4
	COLIN_STATES_EVAIL = 5
	DEAD_ENDS_IDX = 6
	TIME_PER_STATE_EVAL = 7

	def __init__(self, plannerName, problemDomain):
		self.plannerName = plannerName
		self.problemDomain = problemDomain
		self.stats = {}
		self.totalProbs = 0
		self.totalSuccess = 0.0
		self.avgCompTime = 0.0
		self.avgHTime = 0.0
		self.avgStates = 0.0
		self.avgHStates = 0.0
		self.avgColinStates = 0.0
		self.avgDeadEnds = 0.0
		self.avgTimePerStateEval = 0.0

	def getProblemSuccess(self, problem):
		return self.stats[problem][self.SUCCESS_IDX]

	def getProblemCompTime(self, problem):
		return self.stats[problem][self.COMP_TIME_IDX]

	def getProblemHTime(self, problem):
		return self.stats[problem][self.H_TIME_IDX]

	def getProblemStatesEval(self, problem):
		return self.stats[problem][self.STATES_EVAL_IDX]

	def getProblemHStatesEval(self, problem):
		return self.stats[problem][self.H_STATES_EVAL_IDX]

	def getProblemColinStatesEval(self, problem):
		return self.stats[problem][self.COLIN_STATES_EVAIL]

	def getProblemDeadEnds(self, problem):
		return self.stats[problem][self.DEAD_ENDS_IDX]

	def getProblemTimePerStateEval(self, problem):
		return self.stats[problem][self.TIME_PER_STATE_EVAL]

	def createDataStructure(self, problemName):
		if problemName not in self.stats:
			self.stats[problemName] = {}
			self.stats[problemName][self.SUCCESS_IDX] = {}
			self.stats[problemName][self.COMP_TIME_IDX] = {}
			self.stats[problemName][self.H_TIME_IDX] = {}
			self.stats[problemName][self.STATES_EVAL_IDX] = {}
			self.stats[problemName][self.H_STATES_EVAL_IDX] = {}
			self.stats[problemName][self.COLIN_STATES_EVAIL] = {}
			self.stats[problemName][self.DEAD_ENDS_IDX] = {}
			self.stats[problemName][self.TIME_PER_STATE_EVAL] = {}

	def processProblemLog(self, problemName, probNumber, logBuffer):
		self.totalProbs += 1

		self.createDataStructure(problemName)

		#Problem Success
		success = ExtractSuccess.extractValidatorSuccess(logBuffer)		
		self.stats[problemName][self.SUCCESS_IDX][probNumber] = success
		self.totalSuccess += success
		
		#Computational Time
		compTime = ExtractRunningTime.extractPythonRunTime(logBuffer)
		self.stats[problemName][self.COMP_TIME_IDX][probNumber] = compTime
		if compTime is not None:
			self.avgCompTime += compTime
		
		#Heuristic Time
		hTime = ExtractRunningTime.extractHRunTime(logBuffer)
		self.stats[problemName][self.H_TIME_IDX][probNumber] = hTime
		if hTime is not None:
			self.avgHTime += hTime
		
		#States Evaluated
		statesEval, hStates, totalStates = ExtractStatesEval.extractStatesEvaluated(logBuffer)
		self.stats[problemName][self.STATES_EVAL_IDX][probNumber] = statesEval
		self.stats[problemName][self.H_STATES_EVAL_IDX][probNumber] = hStates
		if statesEval is not None:
			self.avgStates += statesEval
		if hStates is not None:
			self.avgHStates += hStates

		#Colin States
		colinStates = ExtractStatesEval.genericExtractStatesEvaluated(logBuffer)
		self.stats[problemName][self.COLIN_STATES_EVAIL][probNumber] = colinStates
		if colinStates is not None:
			self.avgColinStates += colinStates
		
		#Deadends Encountered
		deadEnds = ExtractDeadEnds.extractDeadEndsManually(logBuffer)
		self.stats[problemName][self.DEAD_ENDS_IDX][probNumber] = deadEnds
		if deadEnds is not None:
			self.avgDeadEnds += deadEnds

		#Time Per State Eval
		avgTimePerStateEval = 0
		if colinStates > 0:
			avgTimePerStateEval = compTime / colinStates
		self.stats[problemName][self.TIME_PER_STATE_EVAL][probNumber] = avgTimePerStateEval
		self.avgTimePerStateEval += avgTimePerStateEval