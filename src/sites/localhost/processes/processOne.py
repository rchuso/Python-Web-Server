#!/usr/bin/env python3

'''
Created on 15/03/2020

@author: rand huso
'''

import socket

class Process( object ):
	HOST = '' # should probably be 'localhost' to keep other on the network from connecting to it
	PORT_NUMBER = 7666

	def start( self ):
		with socket.socket(	socket.AF_INET, # IPv4 address
							socket.SOCK_STREAM # for TCP
							) as hostSocket:

			hostSocket.bind(( Process.HOST, Process.PORT_NUMBER ))
			print( 'Creating Process on hostname:port ({}:{})'.format( Process.HOST, Process.PORT_NUMBER ))
			hostSocket.listen( 5 )
			while True:
				count = 0
				clientSocket, clientAddr = hostSocket.accept()
				with clientSocket:
					print( 'connection from:{}'.format( clientAddr ))       
					while True:
						data = clientSocket.recv( 4096 )
						if not data: break # b''
						strData = data.decode( 'utf-8' )
						print( 'Received:{} from {}'.format( strData, clientAddr ))
						count += 1
						if 0 == count%3: strData = strData.title()
						elif 1 == count%3: strData = strData.upper()
						else: strData = strData.lower()
						data = strData.encode( 'utf-8' )
						sendStatus = clientSocket.sendall( data )
						if sendStatus is not None:
							print( 'there was a problem sending the data to {}'.format( clientAddr ))
					print( 'disconnection from:{}'.format( clientAddr ))
			print( 'end of incoming data, closing socket.' )

def main():
	Process().start()

if __name__ == '__main__':
	main()
