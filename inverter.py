import json
import sys
import yaml
from yaml.loader import SafeLoader
from datetime import datetime

import hoymiles

def setupHoymiles(global_config):
    # Load ahoy.yml config file
    try:
        if isinstance(global_config.config_file, str):
            with open(global_config.config_file, 'r') as fh_yaml:
                cfg = yaml.load(fh_yaml, Loader=SafeLoader)
        else:
            with open('ahoy.yml', 'r') as fh_yaml:
                cfg = yaml.load(fh_yaml, Loader=SafeLoader)
    except FileNotFoundError:
        print("Could not load config file. Try --help")
        sys.exit(2)
    except yaml.YAMLError as e_yaml:
        print(
            'Failed to load config frile {global_config.config_file}: {e_yaml}')
        sys.exit(1)

    ahoy_config = dict(cfg.get('ahoy', {}))

    command_queue = {}

    g_inverters = [g_inverter.get('serial')
                   for g_inverter in ahoy_config.get('inverters', [])]
    for g_inverter in ahoy_config.get('inverters', []):
        g_inverter_ser = g_inverter.get('serial')
        command_queue[str(g_inverter_ser)] = []

    # Prepare for multiple transceivers, makes them configurable (currently
    # only one supported)
    try:
        for radio_config in ahoy_config.get('nrf', [{}]):
            hmradio = hoymiles.HoymilesNRF(**radio_config)
        ahoy_config['hmradio'] = hmradio
        ahoy_config['command_queue'] = command_queue
        print('finished radio setup',command_queue)
    except:
        print('could not init radio')
    return ahoy_config

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

def poll_inverter(inverter, retries, ahoy_config):
    """
    Send/Receive command_queue, initiate status poll on inverter

    :param str inverter: inverter serial
    :param retries: tx retry count if no inverter contact
    :type retries: int
    """
    hmradio = ahoy_config['hmradio']
    command_queue = ahoy_config['command_queue']
    inverter_ser = inverter.get('serial')
    dtu_ser = ahoy_config.get('dtu', {}).get('serial')
    try:
        # Queue at least status data request
        command_queue[str(inverter_ser)].append(
            hoymiles.compose_set_time_payload())

        # Putt all queued commands for current inverter on air
        while len(command_queue[str(inverter_ser)]) > 0:
            payload = command_queue[str(inverter_ser)].pop(0)

            # Send payload {ttl}-times until we get at least one reponse
            payload_ttl = retries
            while payload_ttl > 0:
                payload_ttl = payload_ttl - 1
                com = hoymiles.InverterTransaction(
                    radio=hmradio,
                    txpower=inverter.get('txpower', None),
                    dtu_ser=dtu_ser,
                    inverter_ser=inverter_ser,
                    request=next(hoymiles.compose_esb_packet(
                        payload,
                        seq=b'\x80',
                        src=dtu_ser,
                        dst=inverter_ser
                    )))
                response = None
                while com.rxtx():
                    try:
                        response = com.get_payload()
                        payload_ttl = 0
                    except Exception as e_all:
                        pass

            # Handle the response data if any
            if response:
                c_datetime = datetime.now()
                decoder = hoymiles.ResponseDecoder(response,
                                                   request=com.request,
                                                   inverter_ser=inverter_ser
                                                   )
                result = decoder.decode()
                if isinstance(result, hoymiles.decoders.StatusResponse):
                    data = result.__dict__()
                    with open('inverter-data.json', 'w') as convert_file:
                        convert_file.write(json.dumps(data, default=myconverter))
                    return data

    except Exception as e_all:
        # return exampledata:
        # 2022-08-17 08:33:13.870737 Decoded: temp=23.2, pf=1.0 phase0=voltage:237.6, current:0.7, power:17.3, frequency:50.01 string0=voltage:1.2, current:0.01, power:0.0, total:0.0, daily:0 string1=voltage:40.9, current:0.44, power:18.1, total:17.395, daily:18
        print('Iverter Error ',e_all)
        return {
            'temperature': '27',
            'powerfactor': '1.0',
            'phases': [{'voltage': '236.1', 'current': '4', 'power': '100.8', 'frequency': '60'}],
            'strings': [{'voltage': '43', 'current': '1.78', 'power': '74.3', 'energy_total': '27000', 'energy_daily': '400'},
                        {'voltage': '41.4', 'current': '1.08', 'power': '26.5', 'energy_total': '17000', 'energy_daily': '230'}],

        }
