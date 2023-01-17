from web3 import Web3
import logging
import traceback
from functools import wraps
import random
import time
import os


# =============================================admin utils=============================================

# ---------------------------------------------others---------------------------------------------
def convert_to_lower_case(string:str)->str:
	return string.lower()

def convert_to_int(number:str):
	try:
		int_num=int(number)
		return int_num
	except ValueError as ve:
		print('"%s" cannot be converted to an int: %s' % (number, ve))

# ---------------------------------------------math---------------------------------------------

def divby10power3(value):
	return value * 10**(-3)

def mulby10power3(value):
	return value * 10**(3)


# ------------------------------------------web3------------------------------------------

def fromWei(value):
	return Web3.fromWei(value, 'ether')


def convert_to_human_readable(number):
	if isinstance(number,str):
		int_num=convert_to_int(number)
		number=float(int(int_num)*10**-18)
	else:
		number=float(int(number)*10**-18)
	return number

def convert_to_bc_readable(number):
	if isinstance(number,str):
		int_num=convert_to_int(number)
		number=float(int(int_num)*10**18)
	else:
		number=float(int(number)*10**18)
	return number


# ------------------------------------------date/time------------------------------------------

def reformat_date(timestamp:str):
	index=timestamp.find('T')
	date=timestamp[0:index]
	return date


def reformat_time(timestamp:str):
	index=timestamp.find('T')
	time=timestamp[(index+1):-1]
	return time


def randomizer(base,multiplier):
	random_out=base+multiplier*random.random()
	return (random_out)

def rand_amt(number):
	numb=number*random.random()
	return numb

def add_rand_amts(neg,pos):
	amt=int(rand_amt(neg)+rand_amt(pos))
	return amt


def pick_a_random_element(arr):
	return random.choice(arr)

def rand_int_within_bounds(min,max):
	number = random.randint(min,max)
	return number

# =====================================================marginx utils=====================================================
def convert_pair_id_to_chain_id(pair_id:str)->str:
	chain_id = convert_to_lower_case(pair_id.split(":")[0])
	return chain_id


# =====================================================create logger=====================================================

def create_logger(logger_name:str,log_file_name:str):

	# create a logger object 
	logger = logging.getLogger(logger_name) 
	logger.setLevel(logging.INFO)

	# determine the formatting by determining the file extension
	ext = os.path.splitext(log_file_name)[-1].lower()
	if ext == ".csv":
		fmt = '%(asctime)s,%(name)s,%(levelname)s,%(message)s'
	elif ext == ".log":
		fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	datefmt = "%m/%d/%Y %I:%M:%S"
	# create a file to store all the logged exceptions 
	logfile = logging.FileHandler(log_file_name)
	
	formatter = logging.Formatter(fmt,datefmt) 
	
	logfile.setFormatter(formatter) 
	logger.addHandler(logfile)
	
	return logger

# def setup_logger(logger_name, log_file, level=logging.INFO):
#     l = logging.getLogger(logger_name)
#     formatter = logging.Formatter('%(message)s')
#     fileHandler = logging.FileHandler(log_file, mode='w')
#     fileHandler.setFormatter(formatter)
#     streamHandler = logging.StreamHandler()
#     streamHandler.setFormatter(formatter)

#     l.setLevel(level)
#     l.addHandler(fileHandler)
#     l.addHandler(streamHandler)    

# =====================================================decorators======================================================================

def my_timer(orig_func):

	@wraps(orig_func)
	def wrapper(*args,**kwargs):
		t1 = time.time()
		result = orig_func(*args,**kwargs)
		t2 = time.time() - t1

		print('{} ran in: {} sec'.format(orig_func.__name__,t2))
		return result

	return wrapper



def exception_logger(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		try:
			return func(self, *args, **kwargs)
		except:
			issue = "exception in | {} | {} | {} \n".format(self.CLIENT_NAME, self.chain_id, func.__name__)
			issue = issue+"=============================================\n"
			self.system_logger.exception(issue)
			raise
	return wrapper




# def tx_logger(func):
#     @wraps(func)
#     def wrapper(self, *args, **kwargs):
#         self.system_logger.info()
#         return func(self, *args, **kwargs)
#         except:
#             issue = "exception in | {} | {} \n".format(self.CLIENT_NAME, func.__name__)
#             # "exception in "+self.CLIENT_NAME+"-"+func.__name__+"\n"
#             issue = issue+"=============================================\n"
#             self.system_logger.exception(issue)
#             raise
#     return wrapper


# def exception_logger(function):
#     """
#     A decorator that wraps the passed in function and logs 
#     exceptions should one occur
#     """
#     @wraps(function) # this is to allow stacking of decorators
#     def wrapper(*args, **kwargs):
#         try:
#             return function(*args, **kwargs)
#         except Exception as e:
#             logging.error("{} | {} | {} \n {}".format(function.__qualname__, e,type(e),traceback.format_exc()))
#             raise
#     return wrapper