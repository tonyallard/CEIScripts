#!/usr/bin/python3
from pddl.common import POS, AT

class effect:
	pass

class simple_effect(effect):
	def __init__(self, prop, polrty=POS):
		self.proposition = prop
		self.polrty = polrty
	
	def toString(self, tab_depth=0):
		return "{t}{n_h}{prop}{n_f}".format(
			t="\t"*tab_depth,
			n_h="(not " if self.polrty == True else "",
			prop = str(self.proposition),
			n_f=")" if self.polrty == True else ""
		)
	
	def __str__(self):
		return self.toString()

	def __repr__(self):
		return 'simple_effect(proposition={prop}, polrty={polrty})'.format(
			prop = str(self.proposition),
			polrty = self.polrty
		)

class timed_effect(effect):
	def __init__(self, time_spec, effect):
		self.effect = effect
		self.time_spec = time_spec
	
	def toString(self, tab_depth=0):
		return "{t}({ts} {eff})".format(
			t="\t"*tab_depth,
			ts = self.time_spec,
			eff = self.effect.toString()
		)

	def __str__(self):
		return self.toString()

	def __repr__(self):
		return 'timed_effect(time_spec={ts}, effect={eff})'.format(
			ts=self.time_spec,
			eff = self.effect.toString
		)

class timed_initial_literal(timed_effect):
	def __init__(self, time_step, effect):
		super().__init__(AT, effect)
		self.time_step = time_step
	
	def toString(self, tab_depth=0):
		return "{t}(AT {ts} {eff})".format(
			t="\t"*tab_depth,
			ts=self.time_step,
			prop=self.effect.toString()
		)

	def __str__(self):
		return self.toString()

	def __repr__(self):
		return 'timed_initial_literal(time_step={ts}, effect={eff})'.format(
			ts=self.time_step,
			eff = self.effect.toString()
		)

class conj_effect(effect):
	def __init__(self, *effects):
		self.effects = effects
	
	def toString(self, tab_depth=0):
		return "{t}(and \n{eff}\n{t})".format(
			t="\t"*tab_depth,
			eff="\n".join(e.toString(tab_depth+1) for e in self.effects
			)
		)

	def __str__(self):
		return self.toString()

	def __repr__(self):
		return "conj_effect(effects=[{effs}])".format(
			effs=" ".join(e.__repr() for e in self.effects)
		)
	
