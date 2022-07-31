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

PC_PACKET_SIZE = 128

def debug_print(data):
	global debug_Active
	if(True == debug_active):
		print(data)


def send(serial_port, address, sub_address, ack_needed, data_len, data_in, pwd):

	global PC_PACKET_SIZE

	debug_print("Send...")	
	debug_print(address)
	debug_print(sub_address)
	debug_print(ack_needed)
	debug_print(data_len)
	debug_print(data_in)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 0
	
	#address is 4 bytes
	temp_address = address
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] = int(temp_address%256)
	data_counter += 1
	
	#sub_address is 2 bytes
	temp_address = sub_address
	data[data_counter] = int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] = int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	
	#ack_needed is 1 byte
	data[data_counter] = int(ack_needed%256)
	data_counter += 1
	
	#data length here
	# max data len in 36
	
	if(data_len > 56):
		data_len = 56
		
	data[data_counter] = int(data_len%256)
	data_counter += 1
	
	# data
	if(data_len > 0):
		temp_counter = 0
		for temp_char in data_in:
			data[data_counter] = int(temp_char%256)
			data_counter += 1
			temp_counter += 1
			if(temp_counter >= data_len):
				break
	
	# pwd
	data_counter = 64
	temp_pwd = pwd.encode('utf-8')
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
	
	debug_print(data)
	
	#plt = platform.system()

	#if plt == "Windows":
	#	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#else:
	#	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		
	#s.connect(('localhost',socket_number))
	
	serial_port.write(bytes(bytearray(data)))
	
def req_device_info(serial_port, address, pwd):

	global PC_PACKET_SIZE

	debug_print("Radio device request info.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 0
	data_counter += 1
	
	# address
	temp_address = address
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] = int(temp_address%256)
	data_counter += 1
	
	# remote pass
	temp_pwd = pwd.encode('utf-8')
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
		
	debug_print(data)
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))
	
def set_dev_remote_pass(serial_port, address, pwd):

	global PC_PACKET_SIZE
	
	debug_print("Radio set device with Central pass.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 1
	data_counter += 1
	
	# address
	temp_address = address
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] = int(temp_address%256)
	data_counter += 1
	

	# remote pass
	temp_pwd = pwd.encode('utf-8')
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
		
	debug_print(data)	
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))

def set_central_local_pass(serial_port, address, pwd):

	global PC_PACKET_SIZE

	debug_print("Radio set central new pass.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 2
	data_counter += 1	

	# remote pass
	temp_pwd = pwd
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
		
	debug_print(data)	
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))
	
def set_dev_new_local_pass(serial_port, address, pwd, new_pass):

	global PC_PACKET_SIZE
	debug_print("Radio set device with new pass.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 3
	data_counter += 1
	
	# address
	temp_address = address
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] = int(temp_address%256)
	data_counter += 1
	
	# current remote pass
	temp_pwd = pwd.encode('utf-8')
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
		
	# new remote pass
	temp_pwd = new_pass
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
		
	debug_print(data)	
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))

def set_central_channel(serial_port, address, channel):

	global PC_PACKET_SIZE
	debug_print("Radio set Central new channel.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 4
	data_counter += 1

	# Channel Info
	data[data_counter] = channel
	data_counter += 1
	
	debug_print(data)	
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))
	
def save_central_channel(serial_port, address, channel):

	global PC_PACKET_SIZE
	debug_print("Radio save Central new channel.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 5
	data_counter += 1

	# Channel Info
	data[data_counter] = channel
	data_counter += 1

	debug_print(data)	
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))

def set_dev_new_channel(serial_port, address, pwd, channel):

	global PC_PACKET_SIZE
	debug_print("Radio save device new channel.")
	#debug_print(socket_number)
	debug_print(address)

	#Total data length must be 64, this is a radio demand.
	data = PC_PACKET_SIZE*[0]
	data_counter = 4
	
	# Device Info
	data[data_counter] = 6
	data_counter += 1
	
	# address
	temp_address = address
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] =  int(temp_address%256)
	temp_address = int(temp_address/256)
	data_counter += 1
	data[data_counter] = int(temp_address%256)
	data_counter += 1
	
	# Channel Info
	data[data_counter] = channel
	data_counter += 1
	
	# remote pass
	temp_pwd = pwd.encode('utf-8')
	for temp_char in temp_pwd:
		data[data_counter] = temp_char
		data_counter += 1
		
	debug_print(data)	
	serial_port.write(bytes(bytearray(data)))
	debug_print("Send:")
	debug_print(bytes(bytearray(data)))
	
#def main():

	
	
#if __name__ == "__main__":
#	main()
	
	
	
	
	


