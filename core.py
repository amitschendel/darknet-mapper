import socket
import socks
import requests
from bs4 import BeautifulSoup
import mongodb
import datetime
import re


class tor:

    SOCKS_PORT = 9050

    def __init__(self):
        self.setup_tor_connection()

    def setup_tor_connection(self):
        '''
        set the socket to use tor service proxy at port 9050.
        and replace getaddrinfo in custom getaddrinfo which will\
        make the dns query through the socks proxy so it dosn't leak\
        our ip and damage our privacy.
        '''
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.SOCKS_PORT)
        socket.socket = socks.socksocket
        socket.getaddrinfo = self.getaddrinfo

    def setup_original_socket_state(self):
        '''
        return the socket to his default state to use sock type STREAM.
        '''
        socket.socket = socket._realsocket
        socket.getaddrinfo = socket.getaddrinfo

    def getaddrinfo(self, *args):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

    def is_link_exist(self, link):
        '''
        check if link exist
        '''
        self.setup_original_socket_state()
        mongo_client = mongodb.mongo()
        exist = mongo_client.is_link_exist(link)
        self.setup_tor_connection()
        return exist

    def get_unchecked_links(self):
        '''
        get a list of all the unchecked links
        '''
        self.setup_original_socket_state()
        mongo_client = mongodb.mongo()
        unchecked_links = mongo_client.get_unchecked_links()
        self.setup_tor_connection()
        return unchecked_links

    def request_page(self, link, headers):
        '''
        send a get request to the page and return response content
        '''
        try:
            return requests.get(link, headers=headers, timeout=10).text
        except Exception as ex:
            print("Error connecting")
            print(ex)
            return None

    def parse_page(self, page, link):
        '''
        use bs4 to parse the page and extract data,
        take the data and insert it to the database.
        return the links extracted from the website.
        '''
        parser = BeautifulSoup(page, 'html.parser')
        tags = []
        links = []
        mongo_client = mongodb.mongo()
        email_pattern = re.compile(
            r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
        telegram_pattern = re.compile(r"(https://t+\.+me/+[a-zA-Z0-9_.+-]+)")
        bitcoin_pattern = re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$")
        onion_pattern = re.compile(r"[^\s]+\.onion")

        try:
            title = parser.title.string
        except:
            title = None
        try:
            description = parser.find(
                "meta", property="og:description")['content']
        except:
            description = None
        for _link in parser.find_all('a'):
            _link = _link.get('href')
            if _link:
                try:
                    bad_extentions = ['.jpg', '.png', '.pdf', '.doc']
                    # check if the extracted link is not from the same site as the source link
                    source_domain = onion_pattern.findall(link)[0]
                    extracted_domain = onion_pattern.findall(_link)[0]
                    if ".onion" in _link and _link[len(_link)-4:] not in bad_extentions and extracted_domain != source_domain:
                        links.append(_link)
                except:
                    pass
        try:
            tags = mongo_client.add_tags(page)
        except:
            pass
        try:
            date = datetime.datetime.now()
            emails = email_pattern.findall(page)
            telegram_links = telegram_pattern.findall(page)
            bitcoin_wallets = bitcoin_pattern.findall(page)
            self.setup_original_socket_state()
            mongo_client.insert_link_info(link,
                                          title,
                                          description,
                                          emails,
                                          telegram_links,
                                          bitcoin_wallets,
                                          links,
                                          tags,
                                          date
                                          )
            self.setup_tor_connection()
        except Exception as ex:
            print("error inserting data to the database")
            print(ex)
