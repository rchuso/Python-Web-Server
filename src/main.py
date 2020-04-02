#!/usr/bin/env python3

'''
Created on 15/03/2020

@author: rand huso
'''

import time
import logging
import multiprocessing
from backgroundThreads import BackgroundThreads
from servers import SecureServer, SimpleServer

class WebServer( object ):
	HOSTNAME = ''
	PORT_NUMBERS = [6881, 6882]

	def __init__( self ):
		multiprocessing.log_to_stderr( logging.DEBUG )
		logger = multiprocessing.get_logger()
		logger.setLevel( logging.INFO )
		self.processList = []

	def startThisServer( self, server ):
		p = multiprocessing.Process( target=server.start, name='{}'.format( server ))
		p.start()
		self.processList.append( p )

	def startWebServers( self ):
		server = SimpleServer( WebServer.HOSTNAME, WebServer.PORT_NUMBERS[0])
		self.startThisServer( server )
		server = SecureServer( WebServer.HOSTNAME, WebServer.PORT_NUMBERS[1])
		self.startThisServer( server )
		
	def getAddToProcessList( self ):
# 		print( 'getAddToProcessList' )
		def addToProcessList( p ):
# 			print( 'addToProcessList: {}'.format( p.name ))
			self.processList.append( p )
		return addToProcessList

	def stopAllProcesses( self ):
		print( 'stopAllProcesses' )
		for p in self.processList:
			if p.is_alive():
				print( 'stopping {}'.format( p.name ))
				p.terminate() # which signal is now trapped by the code, or use p.kill()
				p.join()

	def showStatus( self ):
		print( 'Process status:' )
		for p in self.processList:
			print( 'is alive:{}\tProcess name:{}'.format( p.is_alive(), p.name ))

	def startBackgroundProcesses( self ):
		backgroundThreads = BackgroundThreads( self.getAddToProcessList())
		backgroundThreads.start()

	def processStopped( self ):
		response = False
		for p in self.processList:
			if not p.is_alive(): response = True
		return response

def main():
	webServer = WebServer()
	webServer.startBackgroundProcesses()
	webServer.startWebServers()
	while True:
		try:
			time.sleep( 300 )
			if webServer.processStopped():
				webServer.showStatus()
				break
		except:
			break
	print( 'main stopping all processes' )
	webServer.stopAllProcesses()

if __name__ == '__main__':
	main()
