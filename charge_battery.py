#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Axitec an GoodWe ET mit Immidiate-Mode laden.
# V1.0 PFu: 28.10.2024
# Scenario: The inverter is used as a unit for power grid energy scheduling.
## schnelles Laden des/der Batteriespeicher vom Netz
## als Parameter den Ziel-SoC angeben
## wird mit 70% der max. Ladeleistung geladen
## diese steht im Register 47603 fast_charging_power
## ist der Ziel-SoC erreicht wird in den Normal-Modus gewechselt
## Aufruf: charge_battery.py 80 für schnelles Laden bis 80%
## wr_0054 = "192.168.20.201"  links
## wr_0052 = "192.168.20.202"  rechts
#Register 35172: total Load of Power (Stromzähler)
#Register 35139: energy that the grid supplies
#Register 35171: energy that the house uses
#Register 35137: energy from the solar system (PV + Battery)

import sys 
import time
import argparse
from pyModbusTCP.client import ModbusClient
import asyncio
import telegram

async def sendmessage(t):
    #bot = telegram.Bot("secret")
    #async with bot:
    #    # kommt im TWC3 Bot an
    #    await bot.send_message(text=t, chat_id=xxxxx)
    #print(t)

bot_info = "Batteriespeicher-Info:"
WR_Liste={"192.168.20.201"}
actual_soc           = 37007     # aktueller Batteriestand
fast_charge_enable   = 47545     # Register zum starten Schnelladen
fast_charge_stop_soc = 47546     # Register bis zu welchem SoC aufladen
fast_charging_power  = 47603     # Ladeleistung in %
total_load_of_power  = 35172     # Aktuelle Last des Stromzählers
stop_soc             = 70        # Default Ziel-Füllstand bei dem Schnell-Laden gestoppt wird


def lese_daten(modbus_host):
    global bot_info
    print("")
    print("get and verify data from ",modbus_host)
    soc = client.read_holding_registers(actual_soc,1)[0]
    fc = client.read_holding_registers(fast_charge_enable,1)[0]
    bot_info = bot_info +"\n\n ist bei "+str(client.read_holding_registers(actual_soc,1)[0])+"%"
    return(soc,fc)

# wurde Parameter mit stop_soc angegeben ?
if len(sys.argv) == 2:
    stop_soc=int(sys.argv[1])

#stop_soc=85  #dummy für Test in idle

# für die beiden GoodWe Wechselrichter ausführen
for mh in WR_Liste:
    client = ModbusClient(host=mh, port=502, timeout=2, unit_id=247)
    aktuell=(lese_daten(mh))    # tuple mit SoC, fast_charge
    # wenn Platz im Speicher ist, dann Schnell-Laden einschalten auf xx %
    if aktuell[0] < stop_soc:
        print(mh,"wird geladen:",aktuell[0],"-->",stop_soc)
        client.write_single_register(fast_charge_enable,1)
        client.write_single_register(fast_charge_stop_soc,stop_soc)
        power=client.read_holding_registers(total_load_of_power,1)
        bot_info = bot_info + "\nwird mit "+str(power[0])+"W vom Grid geladen "+str(aktuell[0])+"-->"+str(stop_soc)
    else:
        print(mh,"Laden nicht notwendig:",aktuell[0],"<--",stop_soc)
        bot_info = bot_info + "\nLaden nicht notwendig "+str(aktuell[0])+"<--"+str(stop_soc)
    print(mh,"fast charging ist",client.read_holding_registers(fast_charge_enable,1)[0])
    bot_info = bot_info + "\nfast charging ist "+str(bool(client.read_holding_registers(fast_charge_enable,1)[0]))
    client.close()
    time.sleep(2)

#print(bot_info)
asyncio.run(sendmessage(bot_info))
