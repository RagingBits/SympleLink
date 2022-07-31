#########################################################################################################
# Developed by Raging Bits. (2022)																		#
# This code is provided free and to be used at users own responsability.								#
#########################################################################################################
import subprocess
import os
import time
import queue 
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
import json
import radio_send_lib
import radio_get_lib
import paho.mqtt.client as mqtt_client
import json_work

debug_active = False
listen_for_radio_run = True
listen_for_radio_running = True

serial_port = serial
radio_input_queue = queue.Queue()
messages_to_radio = queue.Queue()
mqtt_connected = False
jason_radio_configurations_dictionary = json
radio_ok = False


def debug_print(data):
	global debug_active
	if(True == debug_active):
		print(data)

	# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	global device_name
	global mqtt_connected 
	debug_print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
	mqtt_connected = True



def on_message(client, userdata, msg):
	global messages_to_radio
	
	messages_to_radio.put(msg)

# The callback for when a PUBLISH message is received from the server.
def message_to_radio_process(msg):

	global serial_port
	global jason_radio_configurations_dictionary
	global radio_ok

	debug_print("MQTT message in: ")
	debug_print(msg.topic+" "+str(msg.payload))
	
	data_to_device = 0
	data_to_device_len = 0
	try:
#	if(1==1):
		address,sub_address,dir,data_type,ack = json_work.get_dev_info_from_message(jason_radio_configurations_dictionary, msg.topic)
		device_data = json_work.get_device_data_from_address(jason_radio_configurations_dictionary,address)
		address,type,info,pwd,topics = json_work.parse_device_data(device_data)
		
		if(address != 0):
			debug_print("Device found")
		else:
			debug_print("Device not found")
			return 
			
		if(data_type == "NUM"):
			
			int_array_str = msg.payload.split()
			int_array = []
			for val in int_array_str:
				try:
					int_array.append(int(val))
				except:
					int_array.append(int(val,16))

			debug_print(int_array)
			data_to_device = bytes(int_array)
			data_to_device_len = len(data_to_device)
			
		elif(data_type == "STR"):
			data_to_device = bytes(msg.payload)
			data_to_device_len = len(msg.payload)
		elif(data_type == "RAW"):	
			data_to_device = msg.payload
			data_to_device_len = len(msg.payload)
		else:
			pass
			

		if(dir == "IN"):		
			debug_print("Sub address of message:")
			debug_print(str(sub_address))
			if(sub_address == 0xFFFF):
				radio_send_lib.req_device_info(serial_port, address,pwd)
			elif(sub_address == 0xFFFE):
				radio_send_lib.set_dev_remote_pass(serial_port, address,pwd)
			elif(sub_address == 0xFFFD):
				radio_send_lib.set_central_local_pass(serial_port, address, data_to_device)
			elif(sub_address == 0xFFFC):
				radio_send_lib.set_dev_new_local_pass(serial_port, address, pwd, data_to_device)
			elif(sub_address == 0xFFFB):
				radio_send_lib.set_central_channel(serial_port, address, data_to_device[0])
			elif(sub_address == 0xFFFA):
				radio_send_lib.save_central_channel(serial_port, address, data_to_device[0])
			elif(sub_address == 0xFFF9):					
				radio_send_lib.set_dev_new_channel(serial_port, address, pwd, data_to_device[0])
			else:
				ack_needed = 0
				if(ack == '1'):
					ack_needed = 1

				radio_send_lib.send(serial_port, address, sub_address, ack_needed, data_to_device_len, data_to_device,pwd)

			timeout = 50				
			if(ack == '1'):
				timeout *= 4
			while(radio_ok == False and timeout > 0):
				time.sleep(0.1)
				timeout -= 1

			time.sleep(0.5)
			radio_ok = False
	except:
		pass


def listen_for_radio(serial_port,input_queue, mqtt_client):
	
	global listen_for_radio_run
	global listen_for_radio_running
	global radio_ok

	listen_for_radio_running = True
	
	debug_print("Radio receiver thread started.")
	while(listen_for_radio_run == True):
	
		try:
#		if (1==1):
			message,message_data_length = radio_get_lib.listen_for_message(serial_port)
			debug_print("New radio msg in. Len: ")
			debug_print(message_data_length)

			#Process the message
			address, sub_address, data, type = radio_get_lib.message_parser(message)
			debug_print(data) 
			
			if(address == 0 and sub_address == 0 and type == 0):
				radio_ok = True
			else:
				if(type == 2):	
					#Device Info packet
					sub_address = 0xFFFF

				debug_print(address)
				debug_print(sub_address)
				debug_print(type)
				
				#Find if there is a configuration about it.
				device_dat = json_work.get_device_data_from_address(jason_radio_configurations_dictionary,address)
				if(device_dat):
					#Yes, then search for the correct topic.
					device_topic,data_type = json_work.get_message_and_data_type_from_sub_address_and_dir(device_dat, sub_address, "OUT")
					if(device_topic):
						#byteArr = bytearray([b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9'])
						debug_print("Radio data publish: " )
						
						if(data_type == "NUM"):
							bytearr = 0
							potent = 1
							counter = 0
							for val in data:
								if(counter >= message_data_length):
									break
								bytearr += potent * int.from_bytes(val, "big")
								potent *= 256
								counter += 1
						elif(data_type == "INT"):
							bytearr = bytearray()
							counter = 0
							for val in data:
								#debug_print(val)
								#debug_print(bytes(chr(int.from_bytes(val,"big")),'ascii')[0])
								if(counter >= message_data_length):
									break
								bytearr.append(0x20)
								bytearr.append( bytes(str(int.from_bytes(val, "big")),'ascii')[0])
								counter += 1
						elif(data_type == "STR"):
							bytearr = ''
							counter = 0
							for val in data:
								if(counter >= message_data_length):
									break
								if(int.from_bytes(val, "big") != 0):
									bytearr += val.decode('utf-8')
								else:
									break
								counter += 1
						elif(data_type == "RAW"):
							for val in data:
								bytearr += val
						else:
							bytearr = ''
						
						
						
						debug_print(bytearr)
						
						#debug_print( type(data) )
						
						#debug_print(data)
						#Yes there is a topic, just process it and publish it.
						mqtt_client.publish(device_topic,bytearr)
		except:
#		else:
			pass
			#listen_for_radio_run = False
			#debug_print("COM port closed.")
		
		
		
	listen_for_radio_running = False
	debug_print("Radio receiver thread stoped.")

def main():
	
	#Declaration of globals to use.
	global mqtt_connected
	global debug_active
	global jason_radio_configurations_dictionary
	global radio_input_queue
	global serial_port
	global listen_for_radio_run
	global listen_for_radio_running
	global messages_to_radio	
	
	#Declaration of locals to use
	main_loop_run = True
	radio_input_thread = Thread()
	
	#Initialisation of the queues.
	radio_input_queue = queue.Queue()
	messages_to_radio = queue.Queue()

	#Absorb the input arguments.
	parser = argparse.ArgumentParser(description='Radio devices to MQTT services translator.')
	parser.add_argument('-p', metavar='com_port', required=True, help='COM port. (Mandatory argument.)')
	parser.add_argument('-v', metavar='verbose', required=False, help='Verbose mode. (Optional argument.)')
	parser.add_argument('-ip', metavar='broker_ip', required=True, help='Broker IP. (Mandatory argument.)')
	parser.add_argument('-c', metavar='device_list_cfg', required=True, help='Device list JSON configuration. (Mandatory argument.)')
	args = parser.parse_args()
	
	if(args.v):
		debug_active = True
		debug_print("Verbose mode active.")
	
			
	if(not os.path.exists(args.c)):
		debug_print("ERROR: invalid configuration file path.")
		return 
	
	broker_ip = args.ip
	
	debug_print("Radio devices configurations loading...")
	#Load the JSON radio configurations.
	f = open('radio_devices_list.json')
	# Returns JSON object as a dictionary
	jason_radio_configurations_dictionary = json.load(f)
	f.close()
	
	serial_port = serial.Serial(
				port=args.p,
				baudrate=19200,
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.EIGHTBITS,
				timeout=1)
	debug_print("Serial port open.")
	
	
	
	#Start MQTT client
	debug_print("MQTT client starting...")
	client = mqtt_client.Client()	

	client.on_connect = on_connect
	client.on_message = on_message
		
	client.connect(broker_ip, port=1883, keepalive=60, bind_address="")
	debug_print("MQTT client connected to broker: " + str(broker_ip) + ":" + str(1883))
	client.loop_start()
	
	#Start the message input receiver
	radio_input_thread = Thread(target=listen_for_radio, args=(serial_port,radio_input_queue,client))
	radio_input_thread.daemon = True # thread dies with the program
	radio_input_thread.start()
	
	#Subscribe all the radio inputs
	#List all devs
	debug_print("Subscribing radio devices to broker...")
	total_devices = len(jason_radio_configurations_dictionary["DEVICE_LIST"])
	devices_configurations = jason_radio_configurations_dictionary["DEVICE_LIST"]

	#Device by device
	devs_counter = 0
	while(devs_counter < total_devices):
		#get device info
		device_data = json_work.get_device_data_by_index(devices_configurations,devs_counter)
		address,type,info,pwd,topics = json_work.parse_device_data(device_data)
		
		topic_iterate = 0
		total_topics = int(len(topics))
	
		while(topic_iterate < total_topics):
			sub_address,direction,msg,data_type,ack = json_work.parse_device_topic(topics[topic_iterate])
			
			if(direction == "IN"):
				debug_print("Subscribe: " + msg)
				client.subscribe(msg)
			
			topic_iterate += 1
		
		devs_counter += 1
	
	#Start service loop.
	debug_print("Start service.")
	while(main_loop_run == True):
		#if sys.stdin.readline() == 'x\n':
		#	main_loop_run = False

		if(not messages_to_radio.empty()):
			message_to_radio_process(messages_to_radio.get())

		
		time.sleep(0.1)	
			
		
	debug_print("Stoping Serial Port...")	
	listen_for_radio_run = False
	serial_port.close()
	counter = 100
	while(listen_for_radio_running and counter > 0):
		time.sleep(0.1)	
		counter -= 1
	
	debug_print("Disconnecting from broker...")
	client.disconnect()
	debug_print("Closing client...")
	client.loop_stop()

	debug_print("Service ended.")
	
	
if __name__ == "__main__":
	main()
