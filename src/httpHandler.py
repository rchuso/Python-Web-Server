'''
Created on 15/03/2020

@author: rand huso
'''

from http.server import BaseHTTPRequestHandler
from handlers.HandlerFactory import HandlerFactory
from handlers.HandlerHead import HandlerHead
from handlers.HandlerBad import HandlerBad

import cgi

class HttpHandler( BaseHTTPRequestHandler ):
	itemsServed = 0

	def getHostRequest( self ):
		response = None
		if 'Host' in self.headers:
			response = self.headers['Host'].split( ':' )[0]
			if response.startswith( 'www.' ): response = response[4:]
		return response

	def do_GET( self ):
		host = self.getHostRequest()
		handler = HandlerFactory( host, self.path, self.headers )
		self.sendResponse( handler )

	def do_POST( self ):
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
		host = self.getHostRequest()
		self.sendResponse( HandlerHead( host, self.path ))

	def sendResponse( self, handler ):
		if not handler.loadContent():
			handler = HandlerBad( handler.host, handler.path, handler.query, handler.fragment, handler.headers, handler.handlerInfo )
		self.send_response( handler.getStatusCode())
		self.send_header( 'Content-type', handler.getContentType())
		self.end_headers()
		handler.writeContent( self.wfile.write )
		HttpHandler.itemsServed += 1 # not thread-safe, but I don't care
		print( 'items served:{}'.format( HttpHandler.itemsServed ))
