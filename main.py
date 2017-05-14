import argparse
import subprocess
import datetime
import getopt
import requests
import os
import time
import json
import sys
import re

clientID = 'md3wyv2mh57vqm9l655vbqy0b3v8uc'
checkInterval = 30 #keep >= 15 sec

def parse_args():
	""" parses commandline, returns args namespace object """
	desc = ('Check online status of twitch.tv user and start downloading stream when they come online')
	parser = argparse.ArgumentParser(description = desc,
			 formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument('USER', nargs = 1, help = 'twitch.tv username')
	args = parser.parse_args()
	return args

def get_valid_filename(s):
	#borrowed from django
	s = str(s).strip().replace(' ', '_')
	return re.sub(r'(?u)[^-\w.]', '', s)	

def check_user(user):
		# 0: online, 1: offline, 2: not found, 3: error
		statusCode = 3
		url = 'https://api.twitch.tv/kraken/streams/' + user
		response = None
		try:
			r = requests.get(url, headers = {"Client-ID" : clientID}, timeout = 15)
			r.raise_for_status()
			response = r.json()
			if response['stream'] == None:
				statusCode = 1
			else:
				statusCode = 0
		except requests.exceptions.RequestException as e:
			if e.response:
				if e.response.reason == 'Not Found' or e.response.reason == 'Unprocessable Entity':
					statusCode = 2

		return statusCode, response

def mainloop(user):
		while True:
			statusCode, response = check_user(user)
			if statusCode == 1:
				print(user, "currently offline, trying again in", checkInterval, "seconds.")
				time.sleep(checkInterval)
			elif statusCode == 2:
				print("Username not found")
				time.sleep(checkInterval)
			elif statusCode == 3:
				print(datetime.datetime.now().strftime("%Hh%Mm%Ss")," ","unexpected error. will try again in 5 minutes.")
				time.sleep(300)
			elif statusCode == 0:
				print(user, "now online. Stream recording.")
				filename = user + " - " + datetime.datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + " - " + (response['stream']).get("channel").get("status") + ".mp4"
				filename = get_valid_filename(filename)				
				streamURL = "twitch.tv/" + user
				subprocess.call(['streamlink', streamURL, 'best', '-o',  filename ])

				print("Stream finished")
				time.sleep(checkInterval)
				
try:
	user = parse_args().USER[0]
	# print(check_user(user))
	mainloop(user)
except KeyboardInterrupt:
	pass
