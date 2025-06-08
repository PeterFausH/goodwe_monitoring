#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Beschreibung anpassen

# Axitec an GoodWe ET mit BMS-Mode steuern
# V1.0 PFu: 10.04.2025
## netzdienliches Verhalten mit den Batteriespeichern erreichen
## vermeiden dass die Batteriespeicher über Stunden auf 100% stehen
## mache 2 Einträge in Crontab mit links/rechts und on/off
## wr_0054 = "192.168.20.201"  links
## wr_0052 = "192.168.20.202"  rechts
#Register 47000: App_Mode_Index
#Register 47511: EMSPowerModeWrite - 2 charge, 3 discharge, 1 auto/self use mode 8 hold
#Register 47512: Be-/Entladeleistung zwischen 100 und 6500

# experimentell
# hold ging nicht, habe auf discharge gesetzt. Achtung discharge-rate reduzieren
# konnte beobachten dass bei hold das Be-/Entladeresgister eine Rolle spielt.

import sys 
import argparse
from pyModbusTCP.client import ModbusClient
import asyncio
import telegram
import json
import time
from datetime import datetime
#import goodwe
import requests
#import time
#from datetime import date
#from datetime import timedelta
#from datetime import datetime
#from pytz import timezone
import pytz

jetzt = datetime.now()
timezone = pytz.timezone("Europe/Berlin")

discharge = 3   #Entlädt Batteriespeicher
charge   = 4    #Lädt Batteriespeicher von AC/Grid mit hoher Priorität
selfuse  = 1    #Standard-Modus für EBMS System
hold     = 8    #Batterie wird nicht geladen und nicht entladen.
power    = 100  # in Watt, was trotzdem noch rein und raus kann
onoff    = "on" #Default wenn kein Parameter angegeben wird
actual_soc = 37007 #Register für aktuellen SoC

bot_info = "Hier deine Batteriespeicher-Info:\n"


async def sendmessage(t):
    bot = telegram.Bot("secret")
    async with bot:
        # kommt im TWC3 Bot an
        await bot.send_message(text=t, chat_id=0815)


# wurde Parameter links/rechts mit on/off angegeben ?
if len(sys.argv) == 3:
    wr = sys.argv[1]
    onoff=sys.argv[2]
    print(wr,onoff)
else:
    print("kene Parameter angegeben!")
    print("links rechts und on off ist notwendig")
    print(sys.argv[0],"links on")
    print(sys.argv[0],"rechts off")
    #setze default
    wr = "links"
    onoff="on"

# Zustand einsammeln
def lese_daten(modbus_host):
    global bot_info
    global soc_i
    if "201" in modbus_host: ort = "WR 0054 links"
    else: ort = "WR 0052 rechts"
    #print("")
    print("get and verify data from ",modbus_host,ort)
    bot_info = bot_info +"\n"+ ort
    soc_i=client.read_holding_registers(actual_soc,1)[0]
    soc=str(soc_i)+"%"
    print(ort,"37007: Batteriespeicher SoC ist "+soc)
    bot_info = bot_info + ": SoC ist "+soc
    print(ort,"47511: EMSPowerModeWrite war",client.read_holding_registers(47511,1)[0]) # mode 4 ist Laden
    return soc_i

if wr == "links":
    ip = "192.168.20.201"
if wr == "rechts":
    ip = "192.168.20.202"
print(f'IP ist {ip} für {wr}')

# für die Wechselrichter ausführen
client = ModbusClient(host=ip, port=502, timeout=3, unit_id = 247)

lese_daten(ip)

print(" ")
print(wr,":",soc_i)
if onoff == "on":
    if soc_i >= 40:
        print(wr,"Batterie auf HOLD stellen")
        bot_info = bot_info + "\n"+wr+" stelle Batterie auf HOLD"
        client.write_single_register(47511,8)
        client.write_single_register(47512,power)
    else:
        bot_info = bot_info + "\n"+wr+" kein HOLD, Soc nur "+str(soc_i)+"%"
        print(wr,"kein Batterie-HOLD, Soc erst "+str(soc_i)+"%")
        
else:
    print(wr,"ist wieder im Standard Mode")
    bot_info = bot_info + "\n"+wr+" wird nicht gesperrt."
    client.write_single_register(47511,selfuse)
    client.write_single_register(47512,6000)
client.close()
time.sleep(2)

#print(bot_info)
asyncio.run(sendmessage(bot_info))
