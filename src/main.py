#!/usr/bin/env python3

'''
Created on 15/03/2020

@author: rand huso
'''

import time
from server import Server
from backgroundThreads import BackgroundThreads
from http.server import HTTPServer

HOSTNAME = ''
PORT_NUMBER = 6881

class SimpleServer( object ):
	def __init__( self, hostname, portNumber ):
		self.hostname = hostname
		self.portNumber = portNumber
		self.backgroundThreads = BackgroundThreads()

	def startServer( self ):
		self.backgroundThreads.start()
		httpd = HTTPServer(( self.hostname, self.portNumber ), Server )
		print( '{}\t Server Started on {}:{}'.format( time.asctime(), self.hostname, self.portNumber ))
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			pass
		httpd.server_close()
		self.backgroundThreads.stop()

def main():
	server = SimpleServer( HOSTNAME, PORT_NUMBER )
	server.startServer()
	print( '{}\t Server Stopped on {}:{}'.format( time.asctime(), HOSTNAME, PORT_NUMBER ))

if __name__ == '__main__':
	main()
