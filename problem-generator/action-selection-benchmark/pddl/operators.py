#!/usr/bin/python3
from pddl.symbols import operator_symbol

class operator:
	def __init__(self, name, parameters, condition, effect):
		self.name = operator_symbol(name)
		self.parameters = parameters
		self.condition = condition
		self.effect = effect
		
class action(operator):
	def __init__(self, name, parameters, precondition, effect):
		super().__init__(name, parameters, precondition, effect)

	def toString(self, tab_depth=0):
		return """{t}(:action {name}
{t2}:parameters ({params})
{t2}{precond}
{t2}:effect \n{effect}
{t})\n""".format(
	t="\t"*tab_depth,
	t2="\t"*tab_depth,
	name=self.name,
	params=" ".join(self.parameters),
	precond=":precondition \n{cond}".format(cond=self.condition.toString(tab_depth+2)) if self.condition is not None else "",
	effect=self.effect.toString(tab_depth+2)
)

	def __str__(self):
		return self.toString()

class durative_action(operator):
	def __init__(self, name, parameters, duration, condition, effect):
		super().__init__(name, parameters, condition, effect)
		self.duration = duration

	def toString(self, tab_depth=0):
		return """{t}(:durative-action {name}
{t2}:parameters ({params})
{t2}:duration (= ?duration {dur})
{t2}{cond}
{t2}:effect \n{effect}
{t})""".format(
	t="\t"*tab_depth,
	t2="\t"*(tab_depth+1),
	name=self.name,
	params=" ".join(self.parameters),
	dur=self.duration,
	cond=":condition \n{cond}".format(cond=self.condition.toString(tab_depth+2)) if self.condition is not None else "",
	effect=self.effect.toString(tab_depth+2)
)

	def __str__(self):
		return self.toString()