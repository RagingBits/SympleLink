# SympleLink
Symple Link Radio documentation and MQTT bridge example python based.

This repo contains the Symple Link radios documentation and an example on how to use the radios to extend an MQTT network.
The MQTT bridge example is based in python, needing pyserial and paho.mqtt client.

The main file, radio_mqtt_bridge.py needs to be invoked with the following arguments:
-p <serial com port for the Central radio>
-ip <broker ip>
-c <json file with the list of peripheral devices and respective active commands and translation interfaces>

The bridge script will use a json work extractor script called json_work.py, a radio sending packet builder
script called radio_send_lib.py and a radio packet extractor script called radio_get_lib.py

The startup.sh file shows an example of how to invoke the scripts if the broker is running in the local device.

The mosquitto.conf is a simple configuration file in case the local broker is a Mosquitto MQTT service.

The radio_devices_list.json is a simple example of 2 devices and all the possible commands per device. 
The list can be composed of more or less commands, but they need to respect the TAG names and value composition.

Have fun! I did :)
