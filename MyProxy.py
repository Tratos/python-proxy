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

		Info_List=[
					{"IP":"159.153.21.132","printer":Printer.print_it,"generator":None,"virtual":None},#fifa15.service.easports.com
					{"IP":"159.153.228.75","printer":Printer.print_it,"generator":None,"virtual":None},#accounts.ea.com
					{"IP":"159.153.103.28","printer":Printer.print_it,"generator":None,"virtual":None},#reports.tools.gos.ea.com
					{"IP":"104.120.117.43","printer":Printer.print_it,"generator":None,"virtual":None}#fifa15.content.easports.com 
					#"104.95.201.172"#fifa15.content.easports.com       
				  ]
		# ip_list_2=[
		# 			"134.213.37.203",#utas.s2.fut.ea.com
		# 			"104.71.136.11",
		# 			"104.95.111.155",#static-resource.np.community.playstation.net
		# 			"203.105.78.45",
		# 			"23.79.178.172",
		# 			"173.230.217.202",
		# 			"104.71.136.11",#accounts.ea.com
		# 			]
		self.upgrade_socket=False
		if forward_to[1] != 443:
			for dic in Info_List:
				if forward_to[0] == dic["IP"]:
					print "virtual upgrade (gateway)"
					forward_to= (forward_to[0], 443)
					print "ok?"
					self.printer=dic["printer"]
					self.generator=dic["generator"]
					self.virtual=dic["virtual"]
					self.upgrade_socket=True
					break                   
		# for ip in ip_list_2:
		# 	if forward_to[0] == ip:
		# 		self.printer =None
		# 		self.upgrade_socket=False
		# 		break

	def on_forward(self,forward):#forward is the socket connected to the real server  
		if self.upgrade_socket:    
			forward = ssl.wrap_socket(forward)
			print "upgrading to ssl!"

	def on_recv(self,from_socket,to_socket,data):#this mrthod can modifiy the data
		if self.virtual != None:#I haven't see the message of 'modified data' so this'if' calues maybe never matched yet I guess
								#on the other hand it means that the ip of these which has upgrade the virtual has not came in
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
			to_socket=fromsocket#send back	

		
if __name__ == '__main__':
        server = MyProxy('', 8099)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)