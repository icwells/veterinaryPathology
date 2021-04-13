'''Contains age finder class for london zoo data.'''

import re
from string import punctuation

class AgeFinder():

	def __init__(self, digits):
		self.days = re.compile("{}\s?(d|day)".format(digits))
		self.months = re.compile("{}\s?(m|mnths|month)".format(digits))
		self.years = re.compile("{}\s?(y|year)".format(digits))

	def __removePunctuation__(self, val):
		# Removes leading punctuation marks
		if val and val[0] in punctuation:
			val = val[1:]
		return float(val)

	def __checkYear__(self, age):
		# Converts years to months if found
		match = self.years.search(age)
		if match:
			return self.__removePunctuation__(match.group(1)) * 12
		return 0.0

	def __checkMonth__(self, age):
		# Converts years to months if found
		match = self.months.search(age)
		if match:
			return self.__removePunctuation__(match.group(1))
		return 0.0

	def __checkDays__(self, age):
		# Converts years to months if found
		match = self.days.search(age)
		if match:
			d = self.__removePunctuation__(match.group(1))
			if d > 0.0:
				return d / 30
		return 0.0

	def getAge(self, age):
		# Returns age in months
		age = age.replace(";", "")
		ret = self.__checkYear__(age)
		ret += self.__checkMonth__(age)
		ret += self.__checkDays__(age)
		if ret > 0:
			return str(ret)
		return ""

