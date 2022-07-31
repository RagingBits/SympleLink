#########################################################################################################
# Developed by Raging Bits. (2022)																		#
# This code is provided free and to be used at users own responsability.								#
#########################################################################################################
import subprocess
import os
import sys
import time
from multiprocessing import Queue 
import socket,os
from subprocess import PIPE, Popen
from threading  import Thread
import io
import serial
import argparse
import os.path
from pathlib import Path
import sys
import platform 

debug_active = False

def debug_print(data):
	global debug_Active
	if(True == debug_active):
		print(data)


def mem_set(array, value):
	count = len(array)
	while (0 < count):
		count -= 1
		array[count] = value
		
	

parse_input_data = 64*[0]
parse_input_data_length = 0
parse_input_count = 0
parse_input_stage = 0

def serial_input_parser(raw_value_in):

	global parse_input_data
	global parse_input_data_length
	global parse_input_count
	global parse_input_stage

	value = int.from_bytes(raw_value_in, "big")
	#Wait 0xAA
	if(0 == parse_input_stage):
		if(0xAA == value):
			parse_input_stage += 1
	
	#Get data length
	elif(1 == parse_input_stage):
		parse_input_data_length = value
		mem_set(parse_input_data,b'\0')
		parse_input_stage += 1
		parse_input_count = 0
	
	#Get data for the length
	elif(2 == parse_input_stage):
		parse_input_data[parse_input_count] = raw_value_in
		parse_input_count += 1
		
		if(parse_input_count >= parse_input_data_length):
			parse_input_stage += 1
			
	#Get 0x55
	elif(3 == parse_input_stage):
		if(0x55 == value):
		
			parse_input_stage = 0
			#Save packet
			debug_print("New message received")
			return parse_input_data
			
		
	else:
		pass
			
	return 
			

def message_parser(message):

	stage = 0
	counter = 0
	address = 0
	type = 0
	sub_address = 0
	data = []
	for val in message:
		if(0 == stage):
			address = int.from_bytes(val, "big")
			stage += 1
			
		elif(1 == stage):
			address += int.from_bytes(val, "big")*256
			stage += 1
			
		elif(2 == stage):
			address += int.from_bytes(val, "big")*65536
			stage += 1
			
		elif(3 == stage):
			address += int.from_bytes(val, "big")*16777216
			stage += 1
			
		elif(4 == stage):
			type = int.from_bytes(val, "big")
			stage += 1
			
		elif(5 == stage):
			sub_address = int.from_bytes(val, "big")
			stage += 1
			
		elif(6 == stage):
			sub_address += int.from_bytes(val, "big")*256
			stage += 1
			
		else:	
			data.append(val)
			counter+=1
		
	return address, sub_address, data, type
			



def listen_for_message(serial_port):	

	debug_print("Message receiver started.")
	run = True
	raw_message = []
	while(run == True):
		try:
			temp_data = serial_port.read(1)
			debug_print(temp_data)
			raw_message = serial_input_parser(temp_data)
			if(raw_message):
				run = False
		except:
			run = False
			debug_print("COM port ERROR")
		
	debug_print("Message receiver stopped.")
	return raw_message,parse_input_data_length-7

#def main():

	
	
#if __name__ == "__main__":
#	main()
	
	
	
	
	


