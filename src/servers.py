'''
Created on 26/03/2020

@author: rand huso
'''

import os
import ssl
import sys
import time
import signal
from http.server import HTTPServer
from httpHandler import HttpHandler

class ServerBase( object ):
	def __init__( self, hostname, portNumber ):
		self.hostname = hostname
		self.portNumber = portNumber
		def sigHandler( _signo, _stack_frame ):
			self.httpd.server_close()
			sys.exit( 0 )
		signal.signal( signal.SIGTERM, sigHandler )

	def __repr__( self ):
		return '{} on {}:{}'.format( self.__class__.__name__, self.hostname, self.portNumber )

class SimpleServer( ServerBase ):
	def start( self ):
		self.httpd = HTTPServer(( self.hostname, self.portNumber ), HttpHandler )
		print( '{}\t SimpleServer Started on {}:{}'.format( time.asctime(), self.hostname, self.portNumber ))
		self.httpd.serve_forever()

class SecureServer( ServerBase ):
	def start( self ):
		self.httpd = HTTPServer(( self.hostname, self.portNumber ), HttpHandler )
		print( '{}\t SecureServer Started on {}:{}'.format( time.asctime(), self.hostname, self.portNumber ))
		self.httpd.socket = ssl.wrap_socket(	self.httpd.socket,
												keyfile=os.path.abspath( "./key.pem" ),
												certfile=os.path.abspath( './cert.pem' ),
												server_side=True )
		self.httpd.serve_forever()

