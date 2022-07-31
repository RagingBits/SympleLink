#########################################################################################################
# Developed by Raging Bits. (2022)																		#
# This code is provided free and to be used at users own responsability.								#
#########################################################################################################
import subprocess
import os
import time as Time
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
import paho.mqtt.client as mqtt_client
import requests
import datetime
from datetime import *


sunrise_offset = -30
sunset_offset = 30
dim_time = 0
sun_times_request_interval = (12*60)


#Upper Heyford latitude longitude
URL_QUERY = "https://api.sunrise-sunset.org/json?lat=51.9294&lng=1.2796"

#MQTT server 
mqtt_server = "127.0.0.1"


#Device to be handled.
device_power_topic = "IOS_SET_REQUEST-RFCH0-0x00000002"
device_color_topic = "UART_SEND_REQUEST_INT-RFCH0-0x00000002"
device_data_on = "1 1"
device_data_off = "1 0"
#device_data_color100 = "0x55 0xAA 0x09 0xff 0xc0 0x20 0x55 0xAA 0x08 0xff 0xc0 0x20 0x55 0xAA 0x05 0xff 0xc0 0x20 0x55 0xAA 0x03 0xff 0xc0 0x20 0x55 0xAA 0x04 0xff 0xc0 0x20 0x55 0xAA 0x06 0xff 0xc0 0x20 0x55 0xAA 0x02 0xff 0xc0 0x20 0x55 0xAA 0x01 0xff 0xc0 0x20 0x55 0xAA 0x00 0xff 0xc0 0x20"
device_data_color100 = "0x55 0xAA 0x09 0xff 0xc0 0x20 0x55 0xAA 0x08 0xff 0xc0 0x20 0x55 0xAA 0x05 0xff 0xc0 0x20 0x55 0xAA 0x03 0x10 0x00 0xff 0x55 0xAA 0x04 0xff 0xc0 0x20 0x55 0xAA 0x06 0xff 0xc0 0x20 0x55 0xAA 0x02 0xff 0xc0 0x20 0x55 0xAA 0x01 0xff 0xc0 0x20 0x55 0xAA 0x00 0xff 0xc0 0x20"
#device_data_color25 =  "0x55 0xAA 0x09 0x3f 0x30 0x05 0x55 0xAA 0x08 0x3f 0x30 0x05 0x55 0xAA 0x05 0x3f 0x30 0x05 0x55 0xAA 0x03 0x3f 0x30 0x05 0x55 0xAA 0x04 0x3f 0x30 0x05 0x55 0xAA 0x06 0x3f 0x30 0x05 0x55 0xAA 0x02 0x3f 0x30 0x05 0x55 0xAA 0x01 0x3f 0x30 0x05 0x55 0xAA 0x00 0x3f 0x30 0x05"
device_data_color25 =  "0x55 0xAA 0x09 0x3f 0x30 0x05 0x55 0xAA 0x08 0x3f 0x30 0x05 0x55 0xAA 0x05 0x3f 0x30 0x05 0x55 0xAA 0x03 0x10 0x00 0xff 0x55 0xAA 0x04 0x3f 0x30 0x05 0x55 0xAA 0x06 0x3f 0x30 0x05 0x55 0xAA 0x02 0x3f 0x30 0x05 0x55 0xAA 0x01 0x3f 0x30 0x05 0x55 0xAA 0x00 0x3f 0x30 0x05"

debug_active = True

def debug_print(data):
	global debug_active
	if(True == debug_active):
		print(data)

def main():

	global device_topic
	global device_data_on
	global device_data_off
	global device_data_color
	global URL_QUERY
	global mqtt_server
	global sunrise_offset
	global sunset_offset
	global sun_times_request_interval


	sunset_offst = timedelta(minutes = sunset_offset)
	sunrise_offst = timedelta(minutes = sunrise_offset)
	
	
	debug_print("MQTT client starting...")
	client = mqtt_client.Client()	

	#client.on_connect = on_connect
	#client.on_message = on_message
	
	client.connect(mqtt_server, port=1883, keepalive=60, bind_address="")
	debug_print("MQTT client connected to broker: " + str(mqtt_server) + ":" + str(1883))
	
	
	client.loop_start()
	
	run = True
	lights_state_exec = 1
	first_run = True
	
	time_for_url_exec = 1
	sunrise = datetime.strptime('06:00:00', '%H:%M:%S')
	sunset = datetime.strptime('19:00:00', '%H:%M:%S')
	time_now = datetime.strptime('00:00:00', '%H:%M:%S')
	dim_time = datetime.strptime('23:00:00', '%H:%M:%S')
	time_for_url = datetime.strptime('12:00:00', '%H:%M:%S')

	while(run == True):
	
		#Refreshes URL every n minutes.
		if(((time_now >= (time_for_url-timedelta(minutes = 1))) and (time_now <= (time_for_url+timedelta(minutes = 1)))) or (first_run == True)):
			if(time_for_url_exec == 1):
				first_run = False
				time_for_url_exec = 0
				temp_sunset = ''
				temp_sunrise = ''
				retry_get_url = 10
				while(retry_get_url > 0):
					debug_print("Get sun URL")
					requested_info = requests.get(URL_QUERY, timeout=3,verify=False)
					try:
						json_result_list_temp = list(requested_info.json().items())
						
						if(json_result_list_temp[0][0] == 'status'):
							json_result_list = json_result_list_temp[1]
						else:
							json_result_list = json_result_list_temp[0]
	
						#debug_print("Got URL json times:")
						#debug_print(json_result_list)

						json_times_list = list(json_result_list[1].items())
						
	
						#debug_print("Got from url: " + str(json_times_list))
						search_items = 0
						while(search_items < len(json_times_list)):
							#debug_print(json_times_list[search_items][0])
							if(json_times_list[search_items][0] == 'sunrise'):
								temp_sunrise = json_times_list[search_items][1]
	
							elif(json_times_list[search_items][0] == 'sunset'):
								temp_sunset = json_times_list[search_items][1]
					
							else:
								pass
	
							search_items += 1

					except:
						pass

					if(temp_sunset and temp_sunrise):
						sunset = temp_sunset
						sunrise = temp_sunrise
						retry_get_url = 0
					else:
				
						retry_get_url -= 1

	
				if(temp_sunset and temp_sunrise):
	
					debug_print("Sunset Sunrise times updated successfully.")
					debug_print("Next update in " + str(int(sun_times_request_interval/60)) + " hours and " + str(int(sun_times_request_interval%60)) + " minutes")
					debug_print(temp_sunrise)
					debug_print(sunrise)
					debug_print(temp_sunset)
					debug_print(sunset)
				
					sunrise = datetime.strptime(str(sunrise), '%I:%M:%S %p')
					sunset = datetime.strptime(str(sunset), '%I:%M:%S %p')
				
					sunrise_with_ofst = sunrise+sunrise_offst
					sunset_with_ofst = sunset+sunset_offst
			
					sunrise_str = sunrise.strftime('%H:%M:%S')
					sunset_str = sunset.strftime('%H:%M:%S')
			
					sunrise_ofst_str = sunrise_with_ofst.strftime('%H:%M:%S')
					sunset_ofst_str = sunset_with_ofst.strftime('%H:%M:%S')
			
					if(sunrise_offset > 0):
						debug_print("Sunrise at: " + sunrise_str + " +" + str(sunrise_offset) + " minutes")
					else:
						debug_print("Sunrise at: " + sunrise_str + " " + str(sunrise_offset) + " minutes")
				
					if(sunset_offset > 0):
						debug_print("Sunset at: " + sunset_str + " +" + str(sunset_offset) + " minutes")
					else:
						debug_print("Sunset at: " + sunset_str + " " + str(sunset_offset) + " minutes")
				else:
					debug_print("Failed to update Sunset and Sunrise times.")
		
		else:
			time_for_url_exec = 1
			
		#Get time
		time_now = str(datetime.utcnow()).split()[1][:8]
		
		#Convert all to time
		
		time_now =  datetime.strptime(time_now, '%H:%M:%S')
		
		time_now_str = time_now.strftime('%H:%M:%S')
		
		debug_print("Time check: " + time_now_str)


		if(((time_now >= (sunset_with_ofst-timedelta(minutes = 1))) and (time_now <= (sunset_with_ofst+timedelta(minutes = 1)))) or first_run == True):
			#debug_print("->1")
			if(lights_state_exec == 1):
				debug_print("Lights at 100%")
				lights_state_exec = 0
				first_run = False
				client.publish(device_power_topic,device_data_on)
				client.publish(device_color_topic,device_data_color100)
				client.publish(device_color_topic,device_data_color100)

		elif(((time_now >= (sunrise_with_ofst-timedelta(minutes = 1))) and (time_now <= (sunrise_with_ofst+timedelta(minutes = 1)))) or first_run == True):
			#debug_print("->2")
			if(lights_state_exec == 1):
				debug_print("Lights off")
				lights_state_exec = 0
				first_run = False
				client.publish(device_power_topic,device_data_off)
				
		elif(((time_now >= (dim_time-timedelta(minutes = 1))) and (time_now <= (dim_time+timedelta(minutes = 1)))) or first_run == True):
			#debug_print("->3")
			if(lights_state_exec == 1):
				debug_print("Lights at 25%")
				lights_state_exec = 0
				first_run = False
				client.publish(device_power_topic,device_data_on)
				client.publish(device_color_topic,device_data_color25)

		else:
			lights_state_exec = 1

		
		Time.sleep(30)
			
		#while(main_loop_run == True):
		#if sys.stdin.readline() == 'x\n':
		#	main_loop_run = False
		#	Time.sleep(0.1)	
	
	debug_print("Disconnecting from broker...")
	client.disconnect()
	debug_print("Closing client...")
	client.loop_stop()

	debug_print("Service ended.")
	
if __name__ == "__main__":
	main()

