#Used to test ChatClient

import socket

udp_port = 6000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

s.bind(('0.0.0.0',0))

while True:
	print('listening on port:', s.getsockname())
	r = s.recvfrom(1000)
	print("Recieved : %s"%(r[0].decode('utf-8')))
	print(r[1])
	reply = "hey its me!"
	client_address = r[1]
	s.sendto(reply.encode('utf-8'), client_address)  
	print("sent")