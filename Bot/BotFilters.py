from telegram.ext import BaseFilter

class KeyboardFilter(BaseFilter):
	def filter(self, message):
		if message.text in ['Book']:
			return True
		else:
			return False