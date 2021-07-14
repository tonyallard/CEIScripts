#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Class for storing the stats of planners

class PlannerStats():
	
	def __init__(self):
		self.problems = set()
		
		self.SUCCESS_COUNT = {}
		self.FAILED_COUND = {}
		self.SUCCESS_LIST = {}	
		#SEG Faults
		self.SEGMENTATION_FAULT_COUNT = {}
		self.SEGMENTATION_FAULT_LIST = {}	
		#Memory
		self.EXCEEDED_MEMORY_LIMIT_COUNT = {}
		self.EXCEEDED_MEMORY_LIMIT_LIST = {}
		#Time
		self.EXCEEDED_TIME_ALLOCATED_COUNT = {}
		self.EXCEEDED_TIME_ALLOCATED_LIST = {}
		#Unsolvable
		self.PROBLEM_IS_UNSOLVABLE_COUNT = {}
		self.PROBLEM_IS_UNSOLVABLE_LIST = {}
		#Plan Invalid
		self.PLAN_FOUND_IS_INVALID_COUNT = {}
		self.PLAN_FOUND_IS_INVALID_LIST = {}
		#Other
		self.FAILED_FOR_OTHER_REASONS_COUNT = {}
		self.FAILED_FOR_OTHER_REASONS_LIST = {}
	
	def initProblem (self, problem):
		
		self.SUCCESS_COUNT[problem] = 0
		self.FAILED_COUND[problem] = 0
		self.SUCCESS_LIST[problem] = []
		
		#SEG Faults
		self.SEGMENTATION_FAULT_COUNT[problem] = 0
		self.SEGMENTATION_FAULT_LIST[problem] = []	
		#Memory
		self.EXCEEDED_MEMORY_LIMIT_COUNT[problem] = 0
		self.EXCEEDED_MEMORY_LIMIT_LIST[problem] = []
		#Time
		self.EXCEEDED_TIME_ALLOCATED_COUNT[problem] = 0
		self.EXCEEDED_TIME_ALLOCATED_LIST[problem] = []
		#Unsolvable
		self.PROBLEM_IS_UNSOLVABLE_COUNT[problem] = 0
		self.PROBLEM_IS_UNSOLVABLE_LIST[problem] = []
		#Plan Invalid
		self.PLAN_FOUND_IS_INVALID_COUNT[problem] = 0
		self.PLAN_FOUND_IS_INVALID_LIST[problem] = []
		#Other
		self.FAILED_FOR_OTHER_REASONS_COUNT[problem] = 0
		self.FAILED_FOR_OTHER_REASONS_LIST[problem] = []
		
	def incrementSuccess(self, problem):
		self.problems.add(problem)
		self.SUCCESS_COUNT[problem] += 1
		
	def incrementFailure(self, problem):
		self.problems.add(problem)
		self.FAILED_COUND[problem] += 1
		
	def incrementSegFault(self, problem):
		self.problems.add(problem)
		self.SEGMENTATION_FAULT_COUNT[problem] += 1
		
	def incrementMemoryFailure(self, problem):
		self.problems.add(problem)
		self.EXCEEDED_MEMORY_LIMIT_COUNT[problem] += 1
		
	def incrementTimeoutFailure(self, problem):
		self.problems.add(problem)
		self.EXCEEDED_TIME_ALLOCATED_COUNT[problem] += 1
		
	def incrementUnsolvableFailure(self, problem):
		self.problems.add(problem)
		self.PROBLEM_IS_UNSOLVABLE_COUNT[problem] += 1
		
	def incrementInvalidFailure(self, problem):
		self.problems.add(problem)
		self.PLAN_FOUND_IS_INVALID_COUNT[problem] += 1
		
	def incrementOtherFailure(self, problem):
		self.problems.add(problem)
		self.FAILED_FOR_OTHER_REASONS_COUNT[problem] += 1
		
	
	def addSuccessProblem(self, problem, filename):
		self.problems.add(problem)
		self.SUCCESS_LIST[problem].append(filename)
		
	def addSegFaultProblem(self, problem, filename):
		self.problems.add(problem)
		self.SEGMENTATION_FAULT_LIST[problem].append(filename)
		
	def addMemFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.EXCEEDED_MEMORY_LIMIT_LIST[problem].append(filename)
		
	def addTimeoutFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.EXCEEDED_TIME_ALLOCATED_LIST[problem].append(filename)
		
	def addUnsolvableFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.PROBLEM_IS_UNSOLVABLE_LIST[problem].append(filename)
		
	def addInvalidFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.PLAN_FOUND_IS_INVALID_LIST[problem].append(filename)
		
	def addOtherFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.FAILED_FOR_OTHER_REASONS_LIST[problem].append(filename)
