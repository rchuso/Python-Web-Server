'''
Created on 19/03/2020

@author: tazon
'''

import os
import sys
import signal
import importlib
import multiprocessing

class BackgroundThreads( object ):

	def __init__( self, addToProcessList ):
		self.addToProcessList = addToProcessList
		def sigHandler( _signo, _stack_frame ):
			sys.exit( 0 )
		signal.signal( signal.SIGTERM, sigHandler )

	def start( self ):
		siteNames = [ f for f in os.listdir( 'sites' ) if os.path.isdir( os.path.join( 'sites', f ))]
		for site in siteNames:
			siteName = os.path.join( 'sites', site )
			siteFolders = [ f for f in os.listdir( siteName ) if os.path.isdir( os.path.join( siteName, f ))]
			for siteFolder in siteFolders:
				if siteFolder == 'processes':
					processName = os.path.join( siteName, 'processes' )
					processFiles = [ f for f in os.listdir( processName ) if os.path.isfile( os.path.join( processName, f ))]
					for file in processFiles:
						if file.endswith( '.py' ) and file.startswith( 'process' ):
							filePath = os.path.join( processName, file )
							startMethod = self.startProcessClosure( filePath )
							p = multiprocessing.Process( target=startMethod, name='{}'.format( filePath ))
							try:
								p.start()
								self.addToProcessList( p )
							except OSError as ex:
								print( 'OSError starting process:{}: {}'.format( processName, ex ))

	def startProcessClosure( self, filePath ):
		importThis = '{}'.format( filePath[:-3].replace( '/', '.' )) # strip off the .py and connect with dots
		try:
			mod = importlib.import_module( importThis )
			def startProcess():
				obj = mod.Process()
				obj.start()
			return startProcess
		except ImportError as ex:
			print( 'BackgroundThreads::startProcessClosure unable to import {}.. ({})'.format( importThis, ex ))
			raise
