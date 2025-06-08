# collection of python scripts handling goodwe inverter
as I'm using in my installation. Please note, my setup is 3 solar fields connected to 2 inverters an each having a battery pack aside.
Inverters are Goodwe ET6.5 and batteries are axitec 13.5kWh each.

## axitec_hold.py
- `axitec_hold.py links on`
- allows to set an inverter to hold
- if set to hold the charging power is reduced to 100W
- it is set to hold if SoC is above 40%
- if hold is canceled, bms ist set to selfuse and 6000W
- - `axitec_hold.py links off`

## charge_battery.py
- `charge_battery.py 75`
- charges both inverters to target-SoC
- use this if dynamic prices are low in winter

## charge_bms_on_off.py
- uses bms to charge battery from grid
- use this if i'm charging the car while dynamic price is low but don't want to drain the battery
- - `charge_bms_on_off.py "on" 50`
  - keeps the battery in charging mode, discharging is not allowed
- `charge_bms_on_off.py "on" 6500`
- - charges battery with high priority from grid

## single_modbus_goodwe2influx.py
- fetches all values from a goodwe inverter
- writes measurements in a influxdb
- works with dashboards delivered in json `GoodWe_Axited_xx`


 
## goodwe_registerliste.txt
- some notes to registers used in my environment

