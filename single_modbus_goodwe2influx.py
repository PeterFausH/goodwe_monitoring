#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Dank geht an https://github.com/marcelblijleven/goodwe
# Version 1.0    PFu 28.10.2024
# das Script liest die Register vom GoodWe Wechselrichter ein
# und erstellt daraus measurements in einer Influx-Datenbank
# angepasst werden muss:
# die IP-Adresse des Wechselrichters ip_adresse =
# die IP-Adresse des Rechners mit der InfluxDB host =
# die Influx-Datenbank muss angelegt werden

import asyncio
import goodwe
from influxdb import InfluxDBClient

#Konstanten InfluxDB
host = "localhost"
port = 8086
user = "goodwe"
password = "goodwe2010"
dbname = "wechselrichter"
ip_adresse = "192.168.20.201"

# Influx Datenbank verbinden
client = InfluxDBClient(host, port, user, password, dbname)

# json zusammenbauen für Influx-Datenbank
def add(wr,name,wert):
    info=[{"measurement": wr,
           "fields": {name : wert}}]
    #print(info)
    client.write_points(info, time_precision='m')
    return

async def get_runtime_data(wr,ip):
    ip_address = ip
    inverter = await goodwe.connect(ip_address)
    runtime_data = await inverter.read_runtime_data()

    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data:
            if not sensor.id_ == "timestamp":
                if "label" in sensor.id_:
                    print(f'{sensor.id_}="{runtime_data[sensor.id_]}" {sensor.unit}')
                    #print("---------------")
                    data=(f'{runtime_data[sensor.id_]}')
                    add(wr,sensor.id_,data)
                else:
                    #print(f"{sensor.id_}={runtime_data[sensor.id_]} {sensor.unit}")
                    add(wr,sensor.id_,runtime_data[sensor.id_])

# main bei Aufruf über crontab
asyncio.run(get_runtime_data("WR_ET",ip_adresse))

