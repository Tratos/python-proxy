from ProxyServer import TheServer
import Printer
import sys
import ssl

class MyProxy(TheServer):
    def __init__(self,host,port):
        TheServer.__init__(self,host,port)
        upgrade_socket=False #if true the forward connect will be upgraded to ssl
        self.printer=None
        self.generator=None
        self.virtual=None
    def on_accept(self,clientsock,forward_to):#modify the ip or the port here
        #print clientaddr		
        #print forward_to[1]  
        # this is what in webservers is called router /static /index.html
        # [{ip, printer, generator, virtual}...
        # ]
        #Printer.print_it
        Info_List=[
            {"IP":"","printer":Printer.print_it,"generator":None,"virtual":None},#
            {"IP":"","printer":Printer.print_it,"generator":None,"virtual":None},#
            {"IP":"","printer":Printer.print_it,"generator":None,"virtual":None},#
            {"IP":"","printer":Printer.print_it,"generator":None,"virtual":None}#
        ]
        self.upgrade_socket=False
        self.printer=None
        self.generator=None
        self.virtual=None
        if forward_to[1] != 443:
        	for dic in Info_List:
        	    if forward_to[0] == dic["IP"]:
        	        print "virtual upgrade (gateway)"
        	        forward_to[1]  = 443
        	        self.printer   = dic["printer"]
        	        self.generator = dic["generator"]
        	        self.virtual   = dic["virtual"]
        	        self.upgrade_socket=True
        	        break                   
        
    def on_forward(self,forward):#forward is the socket connected to the real server  
        if self.upgrade_socket:     
        	print "upgrading to ssl!"
        	return ssl.wrap_socket(forward)
        else: 
        	return forward
        
    def on_recv(self,from_socket,to_socket,data):#this mrthod can modifiy the data
    									#on the other hand it means that the ip of these which has upgrade the virtual has not came in
        if self.virtual != None:#I haven't see the message of 'modified data' so this'if' calues maybe never matched yet I guess
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
        	from_socket.send(d)	
        	return False#return False will not send this data to the otherend packets
        
        return True
    
	
if __name__ == '__main__':
    server = MyProxy('', 8099)
    try:
        server.main_loop()
    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)
