'''
Created on 15/03/2020

@author: rand huso
'''

import os

from handlers.HandlerImage import HandlerImage
from handlers.HandlerText import HandlerText
from handlers.HandlerBad import HandlerBad

class HandlerFactory():
	handlerTypes =	{
		'html': {'handler': HandlerText,  'type':'html',	'contentType':'text/html',					'bytes': False },
		'css':  {'handler': HandlerText,  'type':'css',		'contentType':'text/css',					'bytes': False },
		'js':   {'handler': HandlerText,  'type':'js',		'contentType':'text/javascript',			'bytes': False },
		'json': {'handler': HandlerText,  'type':'json',	'contentType':'application/json',			'bytes': False },
		'ico':  {'handler': HandlerImage, 'type':'ico',		'contentType':'image/vnd.microsoft.icon',	'bytes': True  },
		'jpg':  {'handler': HandlerImage, 'type':'jpg',		'contentType':'image/jpeg',					'bytes': True  },
		'png':  {'handler': HandlerImage, 'type':'png',		'contentType':'image/png',					'bytes': True  },
				}
	def __new__( self, host, URI, headers, postVars=None ):
		hostQueryFragment = URI.split( '#' ) # will be len=1 if none
		if 1 == len(hostQueryFragment): fragment = None
		else: fragment = hostQueryFragment[1]
		hostQuery = hostQueryFragment[0].split( '?' )
		requestPath = hostQuery[0]
		if '/' == requestPath: requestPath = '/index.html'
		hostSuffix = os.path.splitext( requestPath )
		query = {}
		if 1 < len(hostQuery):
			querySplit = hostQuery[1].split( '&' ) # cheap and dirty
			for qs in querySplit:
				qss = qs.split( '=' )
				query[qss[0]] = qss[1]
		if postVars is not None:
			for postVar in postVars:
				pv = postVar.decode( 'utf-8' )
				val = [ v.decode( 'utf-8' ) for v in postVars[postVar]] # it's an array, for some reason
				query[pv] = val[0] # lose the other information. TODO: could check to see if _is list_
		suffix = hostSuffix[1][1:]

		try:
			if '..' in requestPath:
				response = HandlerBad( host, requestPath, query, fragment, headers, HandlerFactory.handlerTypes['html'] )
			else:
				handlerInfo = HandlerFactory.handlerTypes[suffix]
				response = handlerInfo['handler']( host, requestPath, query, fragment, headers, handlerInfo )
		except KeyError:
			response = HandlerBad( host, requestPath, query, fragment, headers, HandlerFactory.handlerTypes['html'] )
		return response
