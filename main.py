#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hoymiles micro-inverters main application
"""

import sys
import struct
import re
import time
import argparse
from display import displayImage, displayOff, setupDisplay
from draw import drawLines
from inverter import setupHoymiles, poll_inverter
from send import sendData


def main_loop():
    """Main loop"""
    inverters = [
        inverter for inverter in ahoy_config.get('inverters', [])
        if not inverter.get('disabled', False)]

    for inverter in inverters:
        img = drawLines([' ','Checke Daten'])
        displayImage(img, display)
        res = poll_inverter(inverter, 4, ahoy_config)
        if res :
            img = drawLines([f'{res["strings"][0]["power"]}W {res["strings"][0]["energy_daily"]}Wh',
                         f'{res["strings"][1]["power"]}W {res["strings"][1]["energy_daily"]}Wh',
                         f'{(float(res["strings"][0]["energy_total"]) + float(res["strings"][1]["energy_total"]))/1000}kWh',
                         f'Temp:{res["temperature"]}, Übermittle...'])
            print(f'{res["strings"][0]["power"]}W {res["strings"][0]["energy_daily"]}Wh {res["strings"][1]["power"]}W {res["strings"][1]["energy_daily"]}Wh {(float(res["strings"][0]["energy_total"]) + float(res["strings"][1]["energy_total"]))/1000}kWh')
            displayImage(img, display)
            sendStatus = sendData(res,ahoy_config.get('rest_url',''))
            if sendStatus != 200:
                img = drawLines([f'{res["strings"][0]["power"]}W {res["strings"][0]["energy_daily"]}Wh',
                         f'{res["strings"][1]["power"]}W {res["strings"][1]["energy_daily"]}Wh',
                         f'{(float(res["strings"][0]["energy_total"]) + float(res["strings"][1]["energy_total"]))/1000}kWh',
                         f'Übermittlungsfehler {sendStatus}'])
            displayImage(img, display)

        else:
            displayOff(display)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ahoy - Hoymiles solar inverter gateway', prog="hoymiles")
    parser.add_argument("-c", "--config-file", nargs="?", required=True,
                        help="configuration file")
    parser.add_argument("--log-transactions", action="store_true", default=False,
                        help="Enable transaction logging output")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Enable debug output")
    global_config = parser.parse_args()
    ahoy_config = setupHoymiles(global_config)
    display = setupDisplay()
    loop_interval = ahoy_config.get('interval', 1)
    try:
        while True:
            t_loop_start = time.time()

            main_loop()

            print('', end='', flush=True)

            if loop_interval > 0 and (time.time() - t_loop_start) < loop_interval:
                time.sleep(loop_interval - (time.time() - t_loop_start))

    except KeyboardInterrupt:
        sys.exit()
