import sys
import platform 
import json

debug_active = True

def debug_print(data):
	global debug_Active
	if(True == debug_active):
		print(data)
		
def get_subsets_list(raw_set):
	
	sets = list
	total_set_length = len(raw_set)
	#search for first set 
	counter_start = 0
	counter_end = 0
	subset_level = 0
	debug_print("List length: " + str(total_set_length))

	#try:
	
	while(counter_start<total_set_length and counter_start<total_set_length):
		#Search subset start
		searching = True
		while(searching == True and counter_start<total_set_length):
			if(raw_set[counter_start] == '[' and subset_level == 0):
				# Found start
				searching = False
			else:
				if(raw_set[counter_end] == ']'):
					if(subset_level == 0):
						debug_print("ERROR: bad format")
						break
					else:
						subset_level -=1
				counter_start += 1
		
		#Search subset end
		searching = True
		while(searching == True and counter_end<total_set_length):
			if(raw_set[counter_start] == ']' and subset_level == 0):
				# Found end
				searching = False
			else:
				if(raw_set[counter_end] == '['):
					if(subset_level == 0):
						debug_print("ERROR: bad format")
						break
					else:
						subset_level +=1
				counter_start += 1	
	
		set.append(raw_set[counter_start:counter_end])
			
	#except:
	#	pass
		
	return setsv
	
	
		
def get_device_data_by_index(json_dictionary, index):
	total_devices = len(json_dictionary)
	debug_print("Device data by index\n Total devices: " + str(total_devices))
	
	if(index < total_devices):
		return  list(json_dictionary[index].items()) 
		
		
def parse_device_data(json_dictionary):

	total_keys = int(len(json_dictionary))
	debug_print("Parse device data\n Total keys: " + str(total_keys))
	
	address = 0
	type = ""
	info = ""
	password = ""
	topics = []
	
	#Find and absorb the keys
	key_iterate = 0
	while(key_iterate < total_keys):
	
		debug_print("Key: "+ json_dictionary[key_iterate][0])
		if(json_dictionary[key_iterate][0] == "ADDRESS"):
			#Try decimal reading
			try:
				address = int(json_dictionary[key_iterate][1],0)
				debug_print("Address: " + str(address))
			except:
				#Try hexadecimal reading
				try:
					address = int(json_dictionary[key_iterate][1],16)
					debug_print("Address: " + str(address))
				except:
					pass

		elif(json_dictionary[key_iterate][0] == "TYPE"):
			type = json_dictionary[key_iterate][1]
			debug_print("Type: "+json_dictionary[key_iterate][1])
			
		elif(json_dictionary[key_iterate][0] == "INFO"):
			info = json_dictionary[key_iterate][1]
			debug_print("Info: "+json_dictionary[key_iterate][1])
			
		elif(json_dictionary[key_iterate][0] == "PASSWORD"):
			password = json_dictionary[key_iterate][1]
			debug_print("Password: "+json_dictionary[key_iterate][1])
			
		elif(json_dictionary[key_iterate][0] == "TOPICS"):
			topics = json_dictionary[key_iterate][1]
			debug_print("Topics: ")
			debug_print(json_dictionary[key_iterate][1])
		else:
			pass
			
		key_iterate += 1
	return address,type,info,password,topics
	
	
def parse_device_topic(json_dictionary):
	debug_print("Parse device topic\n")
	
	dir = ""
	sub_address = 0
	message = ""
	data_type = ""
	topic_list = list(json_dictionary.items())
	ack = ""	
	total_keys = len(topic_list)
	
	#Find and absorb the keys
	key_iterate = 0
	while(key_iterate < total_keys):
	
		debug_print("Key: ")
		debug_print(topic_list[key_iterate][0])
		if(topic_list[key_iterate][0] == "SUB_ADDR"):
			#Try decimal reading
			debug_print("Value: "+topic_list[key_iterate][1])
			try:
				sub_address = int(topic_list[key_iterate][1],0)
			except:
				#Try hexadecimal reading
				try:
					sub_address = int(topic_list[key_iterate][1],16)
				except:
					pass

		elif(topic_list[key_iterate][0] == "DIR"):
			dir = topic_list[key_iterate][1]
			debug_print("Value: "+topic_list[key_iterate][1])
			
		elif(topic_list[key_iterate][0] == "MSG"):
			message = topic_list[key_iterate][1]
			debug_print("Value: "+topic_list[key_iterate][1])
			
		elif(topic_list[key_iterate][0] == "DATA_TYPE"):
			data_type = topic_list[key_iterate][1]
			debug_print("Value: "+topic_list[key_iterate][1])

		elif(topic_list[key_iterate][0] == "ACK"):
			ack = topic_list[key_iterate][1]
			debug_print("Value: "+topic_list[key_iterate][1])

		else:
			pass
			
		key_iterate += 1
		
	return sub_address,dir,message,data_type,ack
	
def get_device_data_from_address(json_dictionary, address):
	total_devices = len(json_dictionary["DEVICE_LIST"])
	devices_configurations = json_dictionary["DEVICE_LIST"]
	debug_print("Device data from address\n Total devices: " + str(total_devices))
	device_iterate = 0
	while(device_iterate < total_devices):
		#get device info
		device_data = get_device_data_by_index(devices_configurations,device_iterate)
		
		addr,type,info,pwd,topics = parse_device_data(device_data)

		if(addr == address):
			debug_print("success")
			debug_print(device_data)
			return device_data
			
		device_iterate += 1
		
	
def get_message_and_data_type_from_sub_address_and_dir(json_dictionary, sub_add, dir):
		
	debug_print("Message from sub_address and dir\n")

	address,type,info,pwd,topics = parse_device_data(json_dictionary)
	
	total_topics = int(len(topics))
	debug_print("Total topics: " + str(total_topics))
	topic_iterate = 0
	
	while(topic_iterate < total_topics):
	
		sub_address,direction,message,type,ack = parse_device_topic(topics[topic_iterate])
		debug_print("Sub_addr: " + str(sub_address))
		debug_print("Dir: " + direction)
		debug_print("Message: " + message)
		debug_print("Data Type: " + type)
		debug_print("Ack: " + ack)
		if(sub_address == sub_add and dir == direction):
			return message,type
		
		topic_iterate += 1

def get_dev_info_from_message(json_dictionary, message):
		
	debug_print("Sub_address and dir from message\n")

	#List all devs
	total_devices = len(json_dictionary["DEVICE_LIST"])
	devices_configurations = json_dictionary["DEVICE_LIST"]

	#Device by device
	devs_counter = 0
	while(devs_counter < total_devices):
		#get device info
		device_data = get_device_data_by_index(devices_configurations,devs_counter)
		address,type,info,pwd,topics = parse_device_data(device_data)
		
		topic_iterate = 0
		total_topics = int(len(topics))
		
	
		while(topic_iterate < total_topics):
		
			sub_address,direction,msg,type,ack = parse_device_topic(topics[topic_iterate])
			
			if(msg == message):
				return address,sub_address,direction,type,ack
			
			topic_iterate += 1
		
		devs_counter += 1
		
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
		
