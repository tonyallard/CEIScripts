#!/usr/bin/python3
from pddl_symbols import operator_symbol

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
{t2}:precondition {cond}
{t2}:effect {effect}
{t})\n""".format(
	t="\t"*tab_depth,
	t2="\t"*tab_depth,
	name=self.name,
	params=" ".join(self.parameters),
	cond=self.condition.toString(tab_depth+1),
	effect=self.effect.toString(tab_depth+1)
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
{t2}:condition {cond}
{t2}:effect {effect}
{t})""".format(
	t="\t"*tab_depth,
	t2="\t"*(tab_depth+1),
	name=self.name,
	params=" ".join(self.parameters),
	dur=self.duration,
	cond=self.condition.toString(tab_depth+1) if self.condition is not None else "()",
	effect=self.effect.toString(tab_depth+1)
)

	def __str__(self):
		return self.toString()