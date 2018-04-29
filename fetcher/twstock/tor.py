import time
import requests
from stem import Signal
from stem.control import Controller


def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


# signal TOR for a new connection 
def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())

def change_ip():
    session = get_tor_session()
    renew_connection()
    return session
