'''
@author Shyam Sudhakaran

-ARP function that displays helpful info such as IP and mac addresses in a nice format
-UDP discovery that scans the LAN and finds the IP's and ports of peers
-UDP chat program with friendly UI that supports sending/recieving unicast & broadcast messages
'''
from socket import * #sockets
import sys 
import subprocess #used to run arp
import pandas as pd #dataframe
import time
import argparse



def scan():
	s = socket(AF_INET, SOCK_DGRAM) #initialize socket
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #add broadcasting

	ip = '255.255.255.255' #broadcast address

	s.bind(('',0))

	search = True

	i = 6

	ipadds = []
	timeout = time.time() + 60*1 #let run for 1 minutes
	while time.time() < timeout:
		for port in range(10,65535): #check for a ton of ports
			try:
				data = "Hello, you've been scanned"
				#print(port)
				s.sendto(data.encode('utf-8'),(ip,port))
				s.settimeout(0)
				address = s.recvfrom(2000)
				print(address)
				if address[1] in ipadds: #if we already have the address, dont do anything, otherwise add it to the list
					pass
				else:
					ipadds.append(address[1])
			except:
				pass
	ipadds = [x for x in ipadds if x not in [s.getsockname()]]
	return ipadds

def chunk(xs,n): #used to split text into a list of lists
	L = len(xs)
	return [xs[p:p+n] for p in range(0,L,n)]

def discover(command,ext):
	if ext:
		result = subprocess.run([command, '-n'], stdout=subprocess.PIPE) #runs whatever command you put in it
	else:
		result = subprocess.run([command], stdout=subprocess.PIPE) #runs whatever command you put in it
	try:
		output = result.stdout.decode('utf-8') #converts from byte to int
		output = output.splitlines() #splits the string by white space
		output = chunk(output,1)  #splits into lists of corresponding lines
		output = [output[i][0].split() for i in range(0,len(output),1)] #splits each line into a list of their corresponding words
		colnames = output[0] #columnames are the first element
		output = output[1:]
		colnames[2] = colnames[2] + "/Macaddress" #add a little more info for the mac address
		colnames[3:5] = [' '.join(colnames[3:5])] #combine the two columns
		df = pd.DataFrame(output, columns=colnames) #create a nice dataframe that looks like the output of the command line
		return df
	except Exception as e:
		print("No Addresses found!")


def chat(df,sock,arp):

	check = 0

	choice = 0

	while check == 0:
		choice = input("Press 1 for Unicast or 2 for Broadcast: ")
		if choice not in ['1','2']:
			pass
		else:
			check = 1

	check = 0

	while choice == '1': #if you send to one peer
		
		t = True
		print("Peers found by arp:") #print
		print(arp)

		print("Peers (IP,PORT) found by scan: ")	
		for o in df:
			print(o)

		ip = input("Enter an IP Address and corresponding port separated by a column, example: 10.10.10.10,900 : ") #checks if you enter a valid IP
		try: #tries to parse it logically
			ip = ip.split(',')
			ip[1] = int(ip[1])
			tup = tuple(ip)
		except:
			tup = 'not in'

		try:
			udp_ip = tup[0] #get ip and port from tup
			udp_port = tup[1]
			choice = 0
		except:
			t = False
			print("Invalid input! Please enter a valid IP address and Port, in the format IP,Port ")

		while t == True:
			data = input("Enter a Message: ")
			try:
				sock.sendto(data.encode('utf-8'),(udp_ip,udp_port)) #send to the peer
				print("Waiting For Response...")
				sock.settimeout(10.0) #wait 10 seconds
				message = sock.recvfrom(2000) #recieve
				string = "Peer at (IP,Port): " + str(message[1]) + " sent this: " + message[0].decode('utf-8') #print out the message
				print(string)

			except Exception as e:
				print(e)

			while True:
				inp = input("Press 1 to send another message or 0 to return: ")

				if inp == '1':
					break

				elif inp == '0':
					choice = 9 #break out of both while loops
					break

				else:
					print("Invalid! Press 1 to send another message or 0 to return: ")
			if choice == 9: #break here too
				break


	pos = [x[1] for x in df] #ports

	while choice == '2':
		print("Peers found by arp:")
		print(arp)

		print("Peers at (IP,Port) found by scan: ")	
		print(df)
		ip = '255.255.255.255' #broadcast address
		data = input("Enter a Message: ")
		for port in pos: #loop over known ports and send the message to each peer
			try:
				sock.sendto(data.encode('utf-8'),(ip,port))
				print("Waiting For Response...")
				sock.settimeout(5.0) #wait 5 seconds
				message = sock.recvfrom(2000) #recieve
				if message:
					string = "Peer at (IP,Port): " + str(message[1]) + " sent this: " + message[0].decode('utf-8') #print out the message
					print(string)
			except:
				print("No message from Peer at (Port): ", (port))

		while True:
			inp = input("Press 1 to send another message or 0 to return: ")
	
			if inp == '1':
				break

			elif inp == '0':
				choice = 0
				break

			else:
				inp = input("Invalid! Press 1 to send another message or 0 to return: ")


def client(scanbool,discov):

	print("Performing Arp...")
	if discov == True:
		try:
			ipdf = discover('arp','-n')
			df = discover('arp','')

			name = df.ix[:,0]

			ipdf["Name"] = name

			print("Peers found by arp:")
		except:
			ipdf = "No peers found"

		print(ipdf)
		print("Scanning for IP's and ports..")
	else:
		ipdf = "None"
	if scanbool == True:
		tupleips = scan()
	else:
		tupleips = "None"
	print("Peers (IP,PORT) found by scan: ")	
	print(tupleips)

	sock = socket(AF_INET, SOCK_DGRAM ) #initialize socket

	sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #set sock to be able to broadcast

	while True:
		portno = input("Enter a port number or press ENTER to usedefault 23432: ")

		if portno == '':
			portno = 23432

		try:
			sock.bind(('',int(portno)))
			break

		except Exception as e:
			print(e)


	l = 1 #bool for listening
	while True:

		if l != 0:
			inp = input("Press ENTER to start chat, 1 to listen for messages, or 0 to exit: ")

		if inp == '1':
			timeout = time.time() + 60*1 #listen for 1 minute
			while True:
				if time.time() < timeout:
					
					print('listening on:', sock.getsockname())
					try:
						s.settimeout(20)
						message = sock.recvfrom(2000) #recieve 
						string = "Peer at (IP,Port): " + str(message[1]) + " sent this: " + message[0].decode('utf-8') #print out the message
						print(string)			
					except:
						print("No messages recieved")
				else:
					inp = input("Press ENTER to continue listening or press 0 to go back: ")
					if inp == '':
						l = 0
						break
					elif inp == '0':
						l = 1
						break
					else:
						inp = input("Invalid input! Press ENTER to continue listening or press 0 to go back: ")

		if inp == '':

			while True:

				try:
					chat(tupleips,sock,ipdf)
					choice = input("Press 0 to exit, 1 to wait for responses, or press any other key to chat again: ")

					if choice == '0':
						break

					if choice == '1':
						inp = '1'
						break

				except Exception as e:
					raise e

		if inp == '0':
			break

parser=argparse.ArgumentParser( #help
    description='''UDP discovery using ARP and a UDP broadcast packet scanner.
    UDP Chat program with unicast and able to send broadcast messages, and receive responses. Instructions are displayed on the screen as you traverse the program. The program follows this general sequence:\n
    1) Runs arp and puts information in a nice Dataframe'\n'
    2) Scans for peers, this may take some time'\n'
    3) Prompts the user to set the port of the socket(or use the default at 23432)'\n'
    4) prompts user to start a chat(either unicast or broadcast), listen for incoming messages, or just exit the program'\n
    5) don't pass anything to run normally'\n
     ''', 
    )

parser.add_argument('-a', action="store_true", default=False,help='perform arp to find ips with names of devices')
parser.add_argument('-an', action="store_true", default=False,help='perform arp to find ips')
parser.add_argument('-c', action="store", dest="c", type=int,help='multiply integer by 200')
parser.add_argument('-ds',  action="store_true", default=False,help='start chat with just discover')
parser.add_argument('-s',  action="store_true", default=False,help='start chat with just scan')
parser.add_argument('-hello',  action="store_true", default=False,help='Say Hello!')
parser.add_argument('-p', action="store", dest="p", type=int,help='Set a port')

args=parser.parse_args()
if(args.a == True):
	print(discover('arp',''))
if(args.an == True):
	print(discover('arp','-n'))
if(args.c):
	print(args.c*200)
if(args.ds == True):
	client(False,True)
if(args.s == True):
	client(True,False)
if(args.hello == True):
	print("Hey what's up!")
if(args.p):
	s = socket(AF_INET, SOCK_DGRAM) #initialize socket
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #add broadcasting
	s.bind(('',args.p))
	print("New socket bound to port: " + str(args.p))
if not len(sys.argv) > 1:
	client(True,True)










