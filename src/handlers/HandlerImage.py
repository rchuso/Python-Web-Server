'''
Created on 15/03/2020

@author: rand huso
'''

from handlers.HandlerBase import HandlerBase

class HandlerImage( HandlerBase ):
	def __init__( self, host, path, query, fragment, headers, handlerInfo ):
		super( HandlerImage, self ).__init__( host, path, query, fragment, headers, handlerInfo )
