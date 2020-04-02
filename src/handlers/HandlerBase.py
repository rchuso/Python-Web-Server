'''
Created on 15/03/2020

@author: rand huso
'''

import os

class HandlerBase( object ):
	def __init__( self, host, path, query, fragment, headers, handlerInfo ):
		# inputs:
		self.host = host
		self.path = path
		self.query = query
		self.fragment = fragment
		self.headers = headers
		self.handlerInfo = handlerInfo
		# outputs:
		self.statusCode = 200
		self.contentType = handlerInfo['contentType']
		self.content = None

	def loadContent( self ):
		response = True
		if self.path.startswith( '/' ): self.path = self.path[1:]
		if self.path.startswith( 'common' ): fullPath = os.path.join( 'sites', self.path )
		else: fullPath = os.path.join( 'sites', self.host, 'public', self.path )
		if os.path.isfile( fullPath ):
			if self.handlerInfo['bytes']: mode = 'rb'
			else: mode = 'r'
			with open( fullPath, mode ) as fIn:
				self.content = fIn.read()
			self.wrapContent()
			self.runScripts()
			if not self.handlerInfo['bytes']: self.content = bytes( self.content, 'UTF-8' )
		else:
			print( 'HandlerBase::loadContent path:[{}] doesn\'t exist'.format( fullPath ))
			self.statusCode = 404
			response = False
		return response

	def getStatusCode( self ): return self.statusCode
	def getContentType( self ): return self.contentType 
	def runScripts( self ): pass
	def wrapContent( self ): pass

	def writeContent( self, write ):
		if self.content is not None:
			write( self.content )
