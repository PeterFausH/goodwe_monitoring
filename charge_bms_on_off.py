#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Axitec an GoodWe ET mit BMS-Mode laden.
# V1.0 PFu: 28.10.2024
#Scenario: The inverter is used as a unit for power grid energy scheduling.
## PBattery = Xset + PV (Charge)
## Xset refers to the power purchased from the power grid. The power purchased
## from the grid is preferred. If the PV power is too large, the MPPT power will
## be limited. (grid side load is not considered)
## Ich nutze das in Verbindung mit dynamischem Strompreis um in günstigen Zeiten
## das Auto aus dem Netz zu laden -- ohne dabei die Batterie zu entladen:
## charge_bms_on_off.py "on" 500
## lädt die Batterie mit 500W aus dem Netz -> Entladung ist gesperrt.
## mache 2 Einträge in Crontab mit on und off
## wr_0054 = "192.168.20.201"  links
## wr_0052 = "192.168.20.202"  rechts
#Register 35139: energy that the grid supplies
#Register 35171: energy that the house uses
#Register 35172: total Load of Power (Stromzähler)
#Register 35137: energy from the solar system (PV + Battery)
#Register 47000: App_Mode_Index
#Register 47511: EMSPowerModeWrite - 2 charge, 3 discharge, 1 auto/self use mode
#Register 47512, EMSPowerSetWrite - charging/discharging power (in watts)

import sys 
import time
import argparse
from pyModbusTCP.client import ModbusClient
import asyncio
import telegram

async def sendmessage(t):
    #bot = telegram.Bot("secret")
    #async with bot:
        # kommt im TWC3 Bot an
        #await bot.send_message(text=t, chat_id=secret)
    #print(t)

WR_Liste={"192.168.20.201"}
charge =  4    #Lädt Batteriespeicher von AC/Grid mit hoher Priorität
selfuse = 1    #Standard-Modus für EBMS System
power =   5000 #Vorbelegung für Ladeleistung in Watt
onoff =   "on" #Default wenn kein Parameter angegeben wird
actual_soc = 37007 #Register für aktuellen SoC


bot_info = "Hier deine Batteriespeicher-Info:\n"

# wurde Parameter mit on oder off angegeben und mit Ladeleistung?
if len(sys.argv) == 3:
    onoff=sys.argv[1]
    print(onoff)
    power=sys.argv[2]
    print(power)


def lese_daten(modbus_host):
    global bot_info
    print("")
    print("get and verify data from ",modbus_host,ort)
    bot_info = bot_info +"\n"+ ort+" "+modbus_host
    print(mh,"37007: Batteriespeicher SoC ist",client.read_holding_registers(actual_soc,1)[0])
    bot_info = bot_info + "\nSoC ist "+str(client.read_holding_registers(actual_soc,1)[0])+"%"
    print(mh,"47511: EMSPowerModeWrite war",client.read_holding_registers(47511,1)[0]) # mode 4 ist Laden
    print(mh,"47512, EMSPowerSetWrite  war",client.read_holding_registers(47512,1)[0]) # xset ist Ladeleistung
    return


#onoff = "off"
# für die Beiden Wechselrichter ausführen
for mh in WR_Liste:
    client = ModbusClient(host=mh, port=502, timeout=2, unit_id = 247)
    lese_daten(mh) 
    # wenn Parameter on dann Speicherladen einschalten, wenn Parameter off dann Standardmodus
    if onoff == "on":
        print(mh,"wird jetzt vom Grid geladen mit "+ str(power)+"W")
        bot_info = bot_info + "\nwird jetzt vom Grid geladen mit "+ str(power)+"W"
        client.write_single_register(47511,charge)
        client.write_single_register(47512,power)
    else:
        print(mh,"ist wieder im Standard Mode")
        bot_info = bot_info + "\nist wieder im Standard Mode"
        client.write_single_register(47511,selfuse)
        client.write_single_register(47512,1000)
    client.close()
    time.sleep(2)
    
#print(bot_info)
asyncio.run(sendmessage(bot_info))
