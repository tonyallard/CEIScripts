#!/usr/bin/python3

class problem:

	def __init__(self, name, domain):
		self.name = name
		self.domain = domain
		self.objects = []
		self.init = []
		self.goal = None
		self.metric = None

	def toString(self, tab_depth=0):
		return """{t}(define (problem {name})
{t2}(:domain {domain})
{t2}(:objects \n{objs}
{t2})
{t2}(:init \n{init}
{t2})
{t2}(:goal \n{goal}
{t2})
{metric}
{t})""".format(
	t="\t"*tab_depth,
	t2="\t"*(tab_depth+1),
	name = self.name,
	domain = self.domain,
	objs="".join(map(str, self.objects)),
	init="\n".join(f.toString(tab_depth+2) for f in self.init),
	goal=self.goal.toString(tab_depth+2),
	metric=self.metric.toString(tab_depth+1) if self.metric is not None else ""
	)

	def __str__(self):
		return self.toString()
