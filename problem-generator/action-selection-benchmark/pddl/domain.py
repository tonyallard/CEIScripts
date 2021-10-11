#!/usr/bin/python3

class domain:
	def __init__(self, name):
		self.name = name
		self.requirements = []
		self.types = []
		self.predicates = []
		self.functions = []
		self.operators = []

	def toString(self,  tab_depth=0):
		return """{t}(define (domain {name})
{t2}(:requirements {req})
{t2}(:types {types})
{t2}(:predicates 
{preds}
{t2})
{ops}
{t})""".format(
	t="\t"*tab_depth,
	t2="\t"*(tab_depth+1),
	name=self.name,
	req=" ".join(self.requirements),
	types="\n".join(map(str, self.types)),
	preds="\n".join(p.toString(tab_depth+2) for p in self.predicates),
	ops="\n".join(o.toString(tab_depth+1) for o in self.operators)
	)

	def __str__(self):
		return self.toString()

	def __repr(self):
		return "domain(name={name}, requirements=[{reqs}], types=[{types}], predicates=[{preds}], operators=[{ops}])".format(
			namne=self.name,
			reqs=", ".join(self.requirements),
			types=", ".join(map(str, self.types)),
			preds="\n".join(p.toString() for p in self.predicates),
			ops="\n".join(o.toString() for o in self.operators)
		)