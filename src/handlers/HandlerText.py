'''
Created on 15/03/2020

@author: rand huso
'''

import io
import os
import sys

from handlers.HandlerBase import HandlerBase
from html.parser import HTMLParser


class ParseGetTagContents( HTMLParser ):
	def __init__( self, findTag, callback ):
		super( ParseGetTagContents, self ).__init__( convert_charrefs=False )
		self.callback = callback
		self.findTag = findTag
		self.savingData = False

	def handle_starttag( self, tag, attrs ):
		if tag == self.findTag:
			self.savingData = True
		else:
			self.handle_startendtag( tag, attrs, False )

	def handle_endtag( self, tag ):
		if tag == self.findTag:
			self.savingData = False
		else:
			if self.savingData:
				content = '</{}>'.format( tag )
				self.callback( content )

	def handle_startendtag( self, tag, attrs, addEndTag=True ): # must already be saving data, nothing to do if this is the "findTag"
		if self.savingData:
			content = '<{}'.format( tag )
			for attr in attrs:
				if attr[1]: content += ' {}="{}"'.format( attr[0], attr[1])
				else: content += ' {}'.format( attr[0])
			if addEndTag: content += '/>'
			else: content += '>'
			self.callback( content )

	def handle_data( self, data ):
		if self.savingData:
			self.callback( data )


class ParseInsertIntoTemplate( HTMLParser ):
	def __init__( self, source ):
		super( ParseInsertIntoTemplate, self ).__init__( convert_charrefs=False )
		self.source = source
		self.content = ''

	def getAddToContent( self ):
		def addToContent( content ):
			self.content += content
		return addToContent

	def handle_starttag( self, tag, attrs, addEndTag=False ):
		if tag == 'template':
			parseSource = None
			for attr in attrs:
				if 'id' == attr[0]: # must have the id attribute to match with the other file
					parseSource = ParseGetTagContents( attr[1], self.getAddToContent())
			if parseSource is not None: parseSource.feed( self.source )
		else:
			self.content += '<{}'.format( tag )
			for attr in attrs:
				if attr[1]: self.content += ' {}="{}"'.format( attr[0], attr[1])
				else: self.content += ' {}'.format( attr[0])
			if addEndTag: self.content += '/>'
			else: self.content += '>'

	def handle_endtag( self, tag ):
		if tag != 'template':
			self.content += '</{}>'.format( tag )

	def handle_startendtag( self, tag, attrs ):
		self.handle_starttag( tag, attrs, True )

	def handle_data( self, data ):
		self.content += data

	def handle_decl( self, decl ):
		self.content += '<!{}>'.format( decl )


class ParseRunCode( HTMLParser ):
	def __init__( self, callback ):
		super( ParseRunCode, self ).__init__( convert_charrefs=False )
		self.callback = callback
		self.content = ''
		self.code = ''
		self.inCode = False

	def handle_starttag( self, tag, attrs, addEndTag=False ):
		if tag == 'run':
			if not addEndTag:
				self.code = ''
				self.inCode = True
		else:
			item = '<{}'.format( tag )
			for attr in attrs:
				if attr[1]: item += ' {}="{}"'.format( attr[0], attr[1])
				else: item += ' {}'.format( attr[0])
			if addEndTag: item += '/>'
			else: item += '>'
			if self.inCode: self.code += item
			else: self.content += item

	def handle_endtag( self, tag ):
		if tag == 'run':
			self.inCode = False
			self.content += self.callback( self.code )
		else:
			if self.inCode: self.code += '</{}>'.format( tag )
			else: self.content += '</{}>'.format( tag )

	def handle_startendtag( self, tag, attrs ):
		self.handle_starttag( tag, attrs, True )

	def handle_data( self, data ):
		if self.inCode: self.code += data
		else: self.content += data

	def handle_decl( self, decl ):
		self.content += '<!{}>'.format( decl )


class HandlerText( HandlerBase ):
	def __init__( self, host, path, query, fragment, headers, handlerInfo ):
		super( HandlerText, self ).__init__( host, path, query, fragment, headers, handlerInfo )

	def substituteIntoTemplate( self, template ):
		templateParser = ParseInsertIntoTemplate( self.content )
		templateParser.feed( template )
		self.content = templateParser.content

	def getRunCode( self ):
		def runCode( code ): # done as a closure so the right "self" is included
			response = ''
			codeOut = io.StringIO()
			codeErr = io.StringIO()
			sys.stdout = codeOut
			sys.stderr = codeErr
			exec( code, {'self':self} ) # Danger, Will Robinson!
			sys.stdout = sys.__stdout__
			sys.stderr = sys.__stderr__
			if 0 == len( codeErr.getvalue()):
				response = codeOut.getvalue()
			codeOut.close()
			codeErr.close()
			return response
		return runCode

	def runScripts( self ):
		if self.handlerInfo['type'] in ['html','json']:
			myParser = ParseRunCode( self.getRunCode())
			myParser.feed( self.content )
			self.content = myParser.content

	def wrapContent( self ):
		if 'html' == self.handlerInfo['type']:
			localPath = os.path.join( os.path.split( self.path )[0], 'template.html' )
			templateFile = os.path.join( 'sites', self.host, 'public', localPath )
			if os.path.isfile( templateFile ):
				with open( templateFile, 'r' ) as fIn:
					template = fIn.read()
					self.substituteIntoTemplate( template )
