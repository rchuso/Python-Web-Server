'''
Created on 15/03/2020

@author: rand huso
'''

from http.server import BaseHTTPRequestHandler
from handlers.HandlerFactory import HandlerFactory
from handlers.HandlerHead import HandlerHead
from handlers.HandlerBad import HandlerBad

import cgi

class Server( BaseHTTPRequestHandler ):
	itemsServed = 0

	def getHostRequest( self ):
		response = None
		if 'Host' in self.headers:
			print( 'Server::getHostRequest Host:{}'.format( self.headers['Host']))
			response = self.headers['Host'].split( ':' )[0]
			if response.startswith( 'www.' ): response = response[4:]
		return response

	def do_GET( self ):
		print( 'do_GET' )
		host = self.getHostRequest()
		handler = HandlerFactory( host, self.path, self.headers )
		self.sendResponse( handler )

	def do_POST( self ):
		print( 'do_POST' )
		host = self.getHostRequest()
		ctype, pdict = cgi.parse_header( self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postVars = cgi.parse_multipart( self.rfile, pdict )
		elif ctype == 'application/x-www-form-urlencoded':
			length = int( self.headers['content-length'])
			postVars = cgi.parse_qs( self.rfile.read( length ), keep_blank_values=1 )
		else:
			postVars = {}
		handler = HandlerFactory( host, self.path, self.headers, postVars )
		self.sendResponse( handler )

	def do_HEAD( self ):
		print( 'do_HEAD' )
		host = self.getHostRequest()
		self.sendResponse( HandlerHead( host, self.path ))

	def sendResponse( self, handler ):
		if not handler.loadContent():
			handler = HandlerBad( handler.host, handler.path, handler.query, handler.fragment, handler.headers, handler.handlerInfo )
		self.send_response( handler.getStatusCode())
		self.send_header( 'Content-type', handler.getContentType())
		self.end_headers()
		handler.writeContent( self.wfile.write )
		Server.itemsServed += 1 # not thread-safe, but I don't care
		print( 'item count:{}'.format( Server.itemsServed ))
