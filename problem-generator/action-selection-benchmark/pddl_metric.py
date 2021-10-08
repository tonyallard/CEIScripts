#!/usr/bin/python3
from pddl_common import MINIMIZE

class metric:
	def __init__(self, function, optimization=MINIMIZE):
		self.function = function
		self.optimization = optimization

	def toString(self, tab_depth=0):
		return "{t}(:metric {o} {f})".format(
			t="\t"*tab_depth,
			o=self.optimization,
			f=self.function.toString()
		)
	
	def __str__(self):
		return self.toString()

	def __repr__(self):
		return "metric(function={func}, optimization={opt})".format(
			func=self.function.__repr__(),
			opt=self.optimization
		)