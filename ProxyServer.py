import socket
import time 
import select
import re
from struct import *
import struct


SO_ORIGINAL_DST = 80
buffer_size = 4096
delay = 0.0001

class Channel:
    def __init__(self, sin, sout):
        self.sin = sin
        self.sout = sout
        self.initialized = False

    def get_otherend(self, myend):
        if myend == self.sout:
            return self.sin
        else:
            return self.sout

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

class TheServer:# set a mitmproxy 
    input_list = []#this list will contains all the socket
    channel = {}# still don't know 
                # {}is a dictionary in python 

    def __init__(self, host, port):#init a socket that listened on the port of 200 this is the base socket 
        self.port=port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)#means it can accept 200 connects  

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.accept_connect()
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
                    #self.s is in the list of readyinput
                    sock=self.channel[self.s].get_otherend(self.s)#get the other hand of the socket
                    self.on_recv(from_socket=self.s,to_socket=sock,data=self.data)
                    sock.send(self.data)

    #got from pr0cks project https://github.com/n1nj4sec/pr0cks/blob/master/pr0cks.py
    def get_destipport(self, sock):
        odestdata = sock.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
        _, port, a1, a2, a3, a4 = struct.unpack("!HHBBBBxxxxxxxx", odestdata)
        address = "%d.%d.%d.%d" % (a1, a2, a3, a4)
        print('[+] Forwarding incoming connection from %s to %s through the proxy' % (repr(sock.getpeername()), (address, port)))
        #haha when  connected, it seems that always show this message on the screen so find where it used 
        return (address, port)
        

    def accept_connect(self):
        clientsock, clientaddr = self.server.accept()
        forward_to = self.get_destipport(clientsock)
        #modify this hook so you can control the prxoy
        self.on_accept(clientsock=clientsock,forward_to=forward_to)
        
        if forward_to[1] != self.port:
            #setup a tcp socket that is connected to the server end
            forward = Forward().start(forward_to[0], forward_to[1])
        else:
            forward = None

        self.on_forward(forward=forward)#

        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            nchannel = Channel(forward, clientsock)
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

    def on_accept(self,clientsock=None,forward_to=None):
        #show the comming and forwarding sockets
        pass

    def on_recv(self,from_socket=None,to_socket=None,data=None):
        #here we can parse and/or modify the data before send forward
        pass          

    def on_forward(self,forward=None):
        #show the forward socket
        pass

if __name__ == '__main__':
        server = TheServer('', 8099)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)