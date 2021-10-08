#!/usr/bin/python3
from pddl_common import POLARITY
from pddl_common import POS
from pddl_common import NEG

class goal:
	pass

class simple_goal:
	def __init__(self, proposition, polrty=POS):
		self.proposition = proposition
		self.polrty = polrty
	
	def toString(self, tab_depth=0):
		return "{t}{n_h}{prop}{n_f}".format(
			t="\t"*tab_depth,
			n_h="(not " if self.polrty == True else "",
			prop = self.proposition.toString(),
			n_f=")" if self.polrty == True else ""
		)
	
	def __str__(self):
		return self.toString()

	def __repr__(self):
		return 'simple_goal((proposition={prop}, polrty={polrty})'.format(
			prop = str(self.proposition),
			polrty = self.polrty
		)

class timed_goal(simple_goal):
	def __init__(self, time_spec, prop, polrty=POS):
		super().__init__(prop, polrty)
		self.time_spec = time_spec
	
	def toString(self, tab_depth=0):
		return "{t}({ts} {prop})".format(
			t="\t"*tab_depth,
			ts = self.time_spec,
			prop = str(self.proposition)
		)

	def __str__(self):
		return self.toString()

	def __repr__(self):
		return 'timed_goal(time_spec={ts}, proposition={prop}, polrty={polrty})'.format(
			ts=self.time_spec,
			prop = str(self.proposition),
			polrty = self.polrty
		)

class conj_goal(goal):
	def __init__(self, *goals):
		self.goals = goals
	
	def toString(self, tab_depth=0):
		return "{t}(and \n{goal}\n{t})".format(
			t="\t"*tab_depth,
			goal="\n".join(g.toString(tab_depth+1) for g in self.goals)
		)

	def __str__(self):
		return self.toString()

	def __repr__(self):
		return "conj_goal(goals=[{goals}])".format(
			goals=" ".join(g.__repr() for g in self.goals)
		)
	