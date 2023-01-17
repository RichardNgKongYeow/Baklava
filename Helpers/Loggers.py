import os
import logging
from functools import wraps


class Logger():
	def __init__(self, logger_name, logs_file_name):
		self.logger_name = logger_name
		self.logs_file_name = logs_file_name

		# determine the formatting by determining the file extension
		self.fmt = self.set_fmt()
		self.datefmt = self.set_datefmt()

		# self.logger = self.create_logger()        

	def set_fmt(self):
		ext = os.path.splitext(self.logs_file_name)[-1].lower()
		if ext == ".csv":
			fmt = "%(asctime)s,%(name)s,%(levelname)s,%(message)s"
		elif ext == ".log":
			fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
		return fmt

	def set_datefmt(self):
		return "%m/%d/%Y %I:%M:%S"

	def create_logger(self):
		# create a logger object
		logger = logging.getLogger(self.logger_name)
		logger.setLevel(logging.INFO)

		# create a file to store all the logged exceptions
		logfile = logging.FileHandler(self.logs_file_name)

		formatter = logging.Formatter(self.fmt, self.datefmt)

		logfile.setFormatter(formatter)
		logger.addHandler(logfile)

		return logger
	



	# def exception_logger(func):
	# 	@wraps(func)
	# 	def wrapper(self, *args, **kwargs):
	# 		try:
	# 			return func(self, *args, **kwargs)
	# 		except:
	# 			issue = "exception in | {} | {} | {} \n".format(self.CLIENT_NAME, self.chain_id, func.__name__)
	# 			issue = issue+"=============================================\n"
	# 			self.system_logger.exception(issue)
	# 			raise
	# 	return wrapper

# self.system_logger = Logger(configs["logs"]["logger_name"]["system"],configs["logs"]["logs_file_name"]["system"])
# self.monitor_client_logger = Logger(configs["logs"]["logger_name"]["monitor_client"],configs["logs"]["logs_file_name"]["monitor_client"])
# self.manual_client_logger = Logger(configs["logs"]["logger_name"]["manual_client"],configs["logs"]["logs_file_name"]["manual_client"])
# self.tx_logger = Logger(configs["logs"]["logger_name"]["tx"],configs["logs"]["logs_file_name"]["tx"])