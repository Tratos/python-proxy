#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license
import socket
import select
import time
import sys

import datetime
import binascii
from struct import *
import struct
#from cryptography.hazmat.primitives.ciphers.algorithms import SEED

import asyncore, socket
import requests
import ssl

import re

import xml.etree.ElementTree as ET

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001

#mu port is 2100x
#forward_to = ('120.132.76.117', 21001)





class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    

def print_hex_string_nicely(hex_string):
    index = 0
    result = ''
    while hex_string:
        result += '{:08x}: '.format(index)
        index += 16
        line, hex_string = hex_string[:32], hex_string[32:]
        while line:
            two_bytes, line = line[:4], line[4:]
            if two_bytes:
                result += two_bytes + ' '
        result = result[:-1] + '\n'
    print result

def hex_dump_packet(packet_data):
    print_hex_string_nicely(binascii.hexlify(packet_data))

def print_it(x):
    print x

class Channel:
    def __init__(self, sin, sout, virtual=None, generator=None, printer=print_it):
        self.sin = sin
        self.sout = sout
        self.initialized = False
        self.virtual = virtual
        self.generator = generator
        self.printer = printer

    def get_otherend(self, myend):
        if myend == self.sout:
            return self.sin
        else:
            return self.sout

    def procdata(self, dataend, data):
        if dataend == self.sout:
            otherend = self.sin
        else:
            otherend = self.sout
        
        if self.virtual != None:
            if re.match("^(GET|POST|PUT|DELETE|HEAD) .* HTTP/1.1", data):
                k = data.split("\r\n")
                a = k[0].split(" ")
                a[1] = self.virtual[0](a[1])
                k[0] = " ".join(a)
                for a in range(0,len(k)):
                    if k[a].find("Host:") == 0:
                        k[a] = "Host: " + self.virtual[1]
                data = "\r\n".join(k)
                print "modified data!"

        if self.printer != None:
            self.printer(data)

        if self.generator != None:
            print "feeding generated data"
            d = self.generator()
            print d
            dataend.send(d)
            return

        otherend.send(data)

import urlparse

def uri_connect_auth1(u):
    k = urlparse.urlparse(u)
    m = urlparse.parse_qs(k.query)
    client_id = m['access_token'][0]
    token = m['redirect_uri'][0]
    return '/connect/auth?client_id=%s&response_type=code&access_token=%s&redirect_uri=nucleus:rest' % (client_id, token)

def uri_upid(u):
    k = urlparse.urlparse(u)
    m = urlparse.parse_qs(k.query)
    client_id = m['a'][0]
    return '/connect/upidtoken?client_id=%s' % (client_id)

def uri_auth_mobileupid(u):
    k = urlparse.urlparse(u)
    m = urlparse.parse_qs(k.query)
    token = m['a'][0]
    client_id = m['b'][0]
    return '/connect/auth?mobile_login_type=mobile_game_UPID&mobile_UPIDToken=%s&client_id=%s&response_type=code&redirect_uri=nucleus:rest' % (token, client_id)

def upidgen():
    data = 'a6a6a47f-c00f-43f1-b61a-df4a39877b15'
    k = ["HTTP/1.1 200 OK",
    "X-NEXUS-SEQUENCE: 104.236.77.120:1453128487704",
    "X-NEXUS-HOSTNAME: eanprdaccounts04",
    'P3P: CP="ALL DSP COR IVD IVA PSD PSA TEL TAI CUS ADM CUR CON SAM OUR IND"',
    'Pragma: no-cache',
    'Expires: Thu, 01 Jan 1970 00:00:00 GMT',
    'Cache-Control: no-cache',
    'Cache-Control: no-store',
    'Content-Type: text/plain;charset=ISO-8859-1',
    'Content-Length: '+str(len(data)),
    'Date: Mon, 18 Jan 2016 14:48:07 GMT',
    'Server: Powered by Electronic Arts',
    '',
    data]
    return "\r\n".join(k)

def static_blaze():
    data = '<?xml version="1.0" encoding="UTF-8"?>\n<serverinstanceinfo>\n    <address member="0">\n        <valu>\n            <hostname>508454-gosprapp1211.ea.com</hostname>\n            <ip>3561002230</ip>\n            <port>10041</port>\n        </valu>\n    </address>\n    <secure>0</secure>\n    <trialservicename></trialservicename>\n    <defaultdnsaddress>0</defaultdnsaddress>\n</serverinstanceinfo>\n'
    k = ["HTTP/1.1 200 OK",
    "Content-Type: application/xml",
    "X-BLAZE-COMPONENT: redirector",
    "X-BLAZE-COMMAND: getServerInstance",
    "Content-Length: "+str(len(data)),
    "X-BLAZE-SEQNO: 0",
    '', 
    data]
    return "\r\n".join(k)

def blazeserver():
    data="""<?xml version="1.0" encoding="UTF-8"?>
    <serverinstancerequest>
        <blazesdkversion>14.2.1.4.0</blazesdkversion>
        <blazesdkbuilddate>Nov 17 2015 18:36:01</blazesdkbuilddate>
        <clientname>FIFA_15_iOS</clientname>
        <clienttype>CLIENT_TYPE_GAMEPLAY_USER</clienttype>
        <clientplatform>ios</clientplatform>
        <clientskuid>EAX06709607</clientskuid>
        <clientversion>-1</clientversion>
        <dirtysdkversion>14.2.1.4.2</dirtysdkversion>
        <environment>prod</environment>
        <clientlocale>1701729619</clientlocale>
        <name>fifa-2015-ios</name>
        <platform>iPhone</platform>
        <connectionprofile>standardSecure_v4</connectionprofile>
    </serverinstancerequest>"""

    r = requests.post("https://spring14.gosredirector.ea.com:42230/redirector/getServerInstance", data=data, headers = {'User-Agent': 'ProtoHttp 1.3/DS 14.2.1.4.2 (AppleIOS)', 'Content-Type': 'application/xml'}, verify=False).content

    print r
    root = ET.fromstring(r)

    valu = list(root.iter('valu'))[0]
    ip = [a for a in valu if a.tag == 'ip'][0].text
    port = [a for a in valu if a.tag == 'port'][0].text

    host = ".".join([str((int(ip) >> (24 - a*8)) & 255)  for a in range(0,4) ])
    port = int(port)

    return (host, port)

class Forward:# create a socekt that connect to the real server
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

SO_ORIGINAL_DST = 80

class TheServer:# set a mitmproxy 
    input_list = []#this list will contains all the socket
    channel = {}# still don't know 

    def __init__(self, host, port):#init a socket that listened on the port of 200 this is the base socket 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select#
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                try:
                    self.data = self.s.recv(buffer_size)
                except:
                    self.on_close()
                    break

                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    #got from pr0cks project https://github.com/n1nj4sec/pr0cks/blob/master/pr0cks.py
    def get_destipport(self, sock):
        odestdata = sock.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
        _, port, a1, a2, a3, a4 = struct.unpack("!HHBBBBxxxxxxxx", odestdata)
        address = "%d.%d.%d.%d" % (a1, a2, a3, a4)
        print('[+] Forwarding incoming connection from %s to %s through the proxy' % (repr(sock.getpeername()), (address, port)))
        return (address, port)
        


    def on_accept(self):
        clientsock, clientaddr = self.server.accept()
        forward_to = self.get_destipport(clientsock)

        if forward_to[0] == "134.213.69.149":
            forward_to = (forward_to[0], 443)

        if forward_to[0] == "31.13.71.1":
            forward_to[1] = 443

        # if forward_to[0] == "159.153.244.219":
        #     print "feeding static blaze!"
        #     self.input_list.append(clientsock)
        #     nchannel = Channel(None, clientsock, generator=static_blaze)
        #     self.channel[clientsock] = nchannel
        #     return

        virtual = None
        printer = None
        #printer = print_it

        if forward_to[0] == "159.153.21.132":#fifa15.service.easports.com
            print "virtual upgrade (gateway)"
            forward_to= (forward_to[0], 443)

        if forward_to[0] == "159.153.228.75":#fifa15.service.easports.com
            print "virtual upgrade (gateway)"
            forward_to= (forward_to[0], 443)

        if forward_to[0] == "159.153.103.28":#fifa15.service.easports.com
            print "virtual upgrade (gateway)"
            forward_to= (forward_to[0], 443)
        

        # if forward_to[0] == "212.64.148.246":
        #     forward_to = blazeserver()
        #     printer = hex_dump_packet
        

        if forward_to[0] == "1.2.1.1":
            print "virtual upgrade "
            forward_to = ("159.153.228.75", 443)
            l = lambda x: "/connect/token"
            virtual = (l, "accounts.ea.com")
            printer = print_it

        if forward_to[0] == "1.2.1.2":
            print "virtual upgrade "
            forward_to = ("159.153.228.75", 443)
            virtual = (uri_connect_auth1, "accounts.ea.com")
            printer = print_it

        if forward_to[0] == "1.2.1.2":
            print "virtual upgrade "
            forward_to = ("159.153.228.75", 443)
            virtual = (uri_connect_auth1, "accounts.ea.com")
            printer = print_it

        if forward_to[0] == "1.2.1.3":
            print "virtual upgrade "
            forward_to = ("159.153.228.75", 443)
            virtual = (uri_upid, "accounts.ea.com")
            printer = print_it

        if forward_to[0] == "1.2.1.4":
            print "virtual upgrade "
            forward_to = ("159.153.228.75", 443)
            virtual = (uri_auth_mobileupid, "accounts.ea.com")
            printer = print_it
            if False:
                self.input_list.append(clientsock)
                nchannel = Channel(None, clientsock, generator=upidgen)
                self.channel[clientsock] = nchannel
                return

        if forward_to[0] == "1.2.1.5":
            print "virtual upgrade (gateway)"
            forward_to = ("159.153.228.76", 443)
            l = lambda x: "/proxy/identi" + x[1:]
            virtual = (l, "gateway.ea.com")

        if forward_to[1] != 9090:
            #connect the server end
            forward = Forward().start(forward_to[0], forward_to[1])
        else:
            forward = None

        if forward_to[0] == "159.153.244.219":
            print "upgrading to ssl!"
            forward = ssl.wrap_socket(forward)
            printer = print_it
        elif forward_to[0] == "31.13.71.1":
            print "upgrading to ssl!"
            forward = ssl.wrap_socket(forward)
            printer = print_it

        elif forward_to[1] != 80:
            print "upgrading to ssl!"
            forward = ssl.wrap_socket(forward)
            printer = print_it
        

        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            nchannel = Channel(forward, clientsock, virtual, printer=printer)
            self.channel[clientsock] = nchannel
            self.channel[forward] = nchannel
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        
        try:
            name = self.s.getpeername()
        except:
            name = "unknown"
        print name, "has disconnected"

        chan = self.channel[self.s]

        otherend = chan.get_otherend(self.s)

        #remove objects from input_list
        self.input_list.remove(self.s)
        # close the connection with remote server
        self.s.close()
        # delete both objects from channel dict
        del self.channel[self.s]

        if otherend != None:
            self.input_list.remove(otherend)
            # close the connection with client
            otherend.close()  # equivalent to do self.s.close()
            del self.channel[otherend]

    def on_recv(self):
        data = self.data

        #print "got some data"
        # here we can parse and/or modify the data before send forward
        #hex_dump_packet(data)
            
        self.channel[self.s].procdata(self.s, data)

if __name__ == '__main__':
        server = TheServer('', 8099)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)
