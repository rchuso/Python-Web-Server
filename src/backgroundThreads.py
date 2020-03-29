'''
Created on 19/03/2020

@author: tazon
'''

import os
import time
import logging
import importlib
import multiprocessing

class BackgroundThreads( object ):

	def __init__( self ):
		self.processList = []
		multiprocessing.log_to_stderr()
		self.logger = multiprocessing.get_logger()
		self.logger.setLevel( logging.INFO )

	def start( self ):
		siteNames = [ f for f in os.listdir( 'sites' ) if os.path.isdir( os.path.join( 'sites', f ))]
		for site in siteNames:
			siteName = os.path.join( 'sites', site )
			siteFolders = [ f for f in os.listdir( siteName ) if os.path.isdir( os.path.join( siteName, f ))]
			for siteFolder in siteFolders:
				print( 'BackgroundThreads::start examining siteFolder:[{}]'.format( siteFolder ))
				if siteFolder == 'processes':
					processName = os.path.join( siteName, 'processes' )
					processFiles = [ f for f in os.listdir( processName ) if os.path.isfile( os.path.join( processName, f ))]
					for file in processFiles:
						print( 'BackgroundThreads::start examining file:[{}]'.format( file ))
						if file.endswith( '.py' ) and file.startswith( 'process' ):
							filePath = os.path.join( processName, file )
							startMethod = self.startProcessClosure( filePath )
							p = multiprocessing.Process( target=startMethod )
							self.processList.append( p )
							try:
								p.start()
							except OSError as ex:
								print( 'OSError starting process:{}: {}'.format( processName, ex ))

	def startProcessClosure( self, filePath ):
		importThis = '{}'.format( filePath[:-3].replace( '/', '.' )) # strip off the .py and connect with dots
		print( 'BackgroundThreads::startProcessClosure importThis:[{}]'.format( importThis ))
		try:
			mod = importlib.import_module( importThis )
			def startProcess():
				obj = mod.Process()
				obj.start()
			return startProcess
		except ImportError as ex:
			print( 'BackgroundThreads::startProcessClosure unable to import {}.. ({})'.format( importThis, ex ))

	def checkStatus( self ):
		for p in self.processList:
			if not p.is_alive(): return False
		return True

	def stop( self ):
		for p in self.processList:
			if p.is_alive():
				p.terminate()
				p.join()

def main():
	obj = BackgroundThreads()
	obj.start()
	for unused in range( 6 ):
		print( 'check thread list:{}'.format( obj.checkStatus()))
		time.sleep( 6 )
	obj.stop()

if __name__ == '__main__':
	print( 'starting' )
	main()
	print( 'ending' )
