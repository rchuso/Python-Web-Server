'''
Created on 15/03/2020

@author: rand huso
'''

from handlers.HandlerBase import HandlerBase

class HandlerHead( HandlerBase ):
	def __init__( self, host, path, query, fragment, headers, handlerInfo ):
		super( HandlerHead, self ).__init__( host, path, query, fragment, headers, handlerInfo )
