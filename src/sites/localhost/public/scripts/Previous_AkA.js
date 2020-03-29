String.prototype.trim = function() {
	return this.replace(/^\s+|\s+$/g, '');
};

/**
 * written 2008.05.11 as a further experiment in AJAX (long bus rides to and from work).
 * by rand c. huso - based on a previous version from 2003
 * use: add the link for AkA.request() to anything on the xmtml page either manually or
 * by using another script. when the link is clicked, the request is sent off to the
 * server and the response is put on the page.
 */
var AkA = {
		/**
		 * Constants to define the hooks for the web page
		 */
	workingMsgId:'workingMsg',		// ID of the "working" message on the page
	workingOnClass:'workingOn',		// CLASS for showing the message
	workingOffClass:'workingOff',	// CLASS for hiding the message
		/**
		 * Raise the "working" message if there is one on the page.
		 */
	raiseWorking:function() {
//			Log.message( Log.debug, '=========raiseWorking' );
			var workingMsg = document.getElementById( AkA.workingMsgId );
			if( workingMsg ) {
				workingMsg.className = AkA.workingOnClass;
			}
		},
		/**
		 * Lower the "working" message if there is one on the page.
		 */
	dropWorking:function() {
			// Log.message( Log.debug, '=========dropWorking' );
			var workingMsg = document.getElementById( AkA.workingMsgId );
			if( workingMsg ) {
				workingMsg.className = AkA.workingOffClass;
			}
		},
		/**
		 * Timeouts come here - process any errors and remove any "waiting" message.
		 */
	timeout:function( destId ) {
			// Log.message( Log.debug, '=========timeout' );
			destObj = document.getElementById( destId );
			if( destObj ) {
				try{ destObj.xmlHttp.abort(); }catch( e ){}
				AkA.dropWorking();
				if( destObj.siteFun ) destObj.siteFun( false, 'timeout' );
			}
		},
		/**
		 * Handler for state transitions.
		 */
	asyncResponse:function( destId ) {
				/**
				 * The xmlHttp object contains the response - if any. Remove any DOCTYPE line and <?xml?> line
				 * and get the "document" as text/xml.
				 */
			var getXmlDocument = function( source ) {
					// Log.message( Log.debug, '=========getXmlDocument' );
					var removeTagLine = function( source ) {
							// Log.message( Log.debug, '=========removeTagLine length[' + source.length + ']' );
							var xmlLine = source.indexOf( '<?xml' );
							if( -1 == xmlLine ) return source;
							var xmlLineEnds = source.indexOf( '?>' );
							return source.substring( 2+xmlLineEnds ).trim();
						}
					var removeDoctype = function( source ) {
							// Log.message( Log.debug, '=========removeDoctype length[' + source.length + ']' );
							var docTypeBegins = source.indexOf( '<!DOCTYPE' );
							if( -1 == docTypeBegins ) return source;
							var docTypeEnds = source.indexOf( '>', docTypeBegins );
							return source.substring( 1+docTypeEnds ).trim();
						};
					var responseText = removeDoctype( source );
					responseText = removeTagLine( responseText );
					responseText = responseText.trim();
					// Log.message( Log.info, 'responseText[' + responseText + ']' );
					var doc = null;
					try {
						var parser = new DOMParser();
						// Log.message( Log.info, 'have DOMParser... attempting to parse as text/html' );
						doc = parser.parseFromString( responseText, "application/xml" );
						// Log.message( Log.info, 'parsed?[' + doc + ']' );
					} catch( e ) {
						try {
							doc = new ActiveXObject( 'Microsoft.XMLDOM' );
							doc.async = false;
							doc.loadXML( responseText );
						} catch( e ) {
							LogMessage( Log.Debug, 'Fatal! Cannot create parser for response.' );
							doc = null;
						}
					}
					return doc;
				};
				/**
				 * The response may be JSON, or it may be xhtml or xml in text form.
				 */
			var useTextResponse = function( destObj, source ) {
					// Log.message( Log.debug, '=========useTextResponse[' + source.trim() + ']' );
					if( 0 == source.trim().indexOf( '{' )) {
						var jsonData = eval( '(' + source.trim() + ')' );
						return jsonData;
					} else {
						var xmlSource = getXmlDocument( source );
						// Log.message( 'XmlDocument[' + xmlSource + ']' );
						if( xmlSource ) return useXmlResponse( destObj, xmlSource );
					}
					return source;
				};
				/**
				 * Identify the source node by "id" - look at attributes because xml documents
				 * don't have getElementById
				 */
			var getXmlElementById = function( destId, source ) {
					// Log.message( Log.debug, '=========getXmlElementById find[' + destId + '] in source['
//					+ source.nodeName + '] childNodes[' + source.childNodes.length + ']' );
					var attr = source.attributes; // difficulty on Opera
					if( attr ) {
						var checkId = attr.getNamedItem( 'id' );
						if( checkId ) {
							// Log.message( Log.info, 'getXmlElementById attributes[' + checkId + '] found[' + checkId.value + ']==[' + destId + ']' );
							if( checkId.value == destId ) {
								return source;
							}
						}
					}
					var response = null;
					for( var i=0; i<source.childNodes.length; ++i ) {
						response = getXmlElementById( destId, source.childNodes.item(i));
						if( response ) return response;
					}
					return response;
				};
				/**
				 * Manually copy all the source nodes to the destination
				 */
			var copySrcNodes = function( dest, src ) {
					// Log.message( Log.debug, '=========copySrcNodes' );
					for( var i=0;i<src.length; ++i ) {
						copySrcToDest( dest, src[i]);
					}
				};
				/**
				 * Individually copy elements, attributes, and text -=- I had some difficulty with
				 * cloneNode for xml documents
				 */
			var copySrcToDest = function( dest, src ) {
					// Log.message( Log.debug, '=========copySrcToDest' );
					switch( src.nodeType ) {
						case 1:
							var newNode = document.createElement( src.nodeName );
							for( var i=0; i<src.attributes.length; ++i ) {
								copySrcToDest( newNode, src.attributes.item(i));
							}
							for( var i=0; i<src.childNodes.length; ++i ) {
								copySrcToDest( newNode, src.childNodes.item(i) )
							}
							dest.appendChild( newNode );
							break;
						case 2:
							dest.setAttribute( src.nodeName, src.nodeValue );
							break;
						case 3:
							if( src.nodeValue && 0 < src.nodeValue.trim().length ) {
								var newText = document.createTextNode( src.nodeValue.trim());
								dest.appendChild( newText );
							}
							break;
					}
				};
				/**
				 * Use the supplied response (in "source"). Lower the "working" message. Then remove any content
				 * already in place and copy across the new content.
				 */
			var useXmlResponse = function( destObj, source ) {
					// Log.message( Log.debug, '=========useXmlResponse[' + destObj + '][' + source + ']' );
					var srcNode;
					try {
						srcNode = getXmlElementById( destObj.id, source);
					} catch(e){}
					if( !srcNode ) {
						try {
							srcNode = source.getElementById( destObj.id );
						} catch(e){}
					}
					// Log.message( Log.info, 'useXmlResponse srcNode[' + srcNode + ']' );
					if( !srcNode ) return false;
					copySrcNodes( destObj, srcNode.childNodes );
					return true;
				};
				/**
				 * Debug tool to display the node tree
				 */
			var showTree = function( source ) {
					// Log.message( Log.debug, '=========showTree type[' + source.nodeType + '] childNodes[' + source.childNodes.length + ']' );
					switch( source.nodeType ) {
						case 1:
							// Log.message( Log.debug, '=========1 node[' + source.nodeName + '], with[' + source.childNodes.length + '] nodes' );
							for( var i=0; i<source.attributes.length; ++i ) {
								showTree( source.attributes.item(i));
							}
							for( var i=0; i<source.childNodes.length; ++i ) {
								showTree( source.childNodes.item(i));
							}
							break;
						case 2:
							// Log.message( Log.debug, '=========2 attribute[' + source.nodeName + ']=[' + source.nodeValue + ']' );
							break;
						case 3:
							if( source.nodeValue && 0 < source.nodeValue.trim().length ) {
								// Log.message( Log.debug, '=========3 text[' + source.nodeValue.trim() + ']' );
							}
							break;
						case 7:
							// Log.message( Log.debug, '=========7 processing instruction[' + source.firstChild + ']-ignore' );
							break;
						case 9:
							// Log.message( Log.debug, '=========9 document[' + source.firstChild + ']' );
							for( var i=0; i<source.childNodes.length; ++i ) {
								showTree( source.childNodes.item(i));
							}
							break;
						default:
								// Log.message( Log.debug, '=========' + source.nodeType + '] UNUSED name[' + source.nodeName + '] value[' + source.nodeValue + ']' );
							break;
					}
				};
			var removeOldTree = function( destObj ) {
					// Log.message( Log.debug, '=========removeOldTree' );
					while( destObj.firstChild ) {
						destObj.removeChild( destObj.firstChild );
					}
				};
		// asyncResponse -- begin here
			destObj = document.getElementById( destId );
			if( destObj ) {
				switch(destObj.xmlHttp.readyState ) {
					case 4:
						// Log.message( Log.info, 'responseXml[' + destObj.xmlHttp.responseXML + '] responseText[' + destObj.xmlHttp.responseText + ']' );
						clearTimeout( destObj.timeout );
						AkA.dropWorking();
						// could check destObj.xmlHttp.status != 200 && != 304 (Opera)
						if( destObj.hasAttribute ) { // let's just say that IE needs to grow up
							if( !destObj.hasAttribute( 'doNotReplace' )) removeOldTree( destObj );
						} else if( !destObj.doNotReplace ) {
							removeOldTree( destObj );
						}
						var success = false;
						// see what's available
						try{
							success = useXmlResponse( destObj, destObj.xmlHttp.responseXML );
						}catch( e ) {}
						if( !success && destObj.xmlHttp.responseText ) {
							try{
								success = useTextResponse( destObj, destObj.xmlHttp.responseText );
							}catch( e ) {
								Log.message( Log.warn, 'exception with TextResponse\n[' + e.name + ']\n[' + e.message + ']' );
							}
						}
						if( destObj.siteFun )  {
							destObj.siteFun( success );
						}
						break;
					case 0: // Uninitialized -=- open not called yet
					case 1: // Loading -=- object is created
					case 2: // Loaded -=- after "send"
					case 3: // Interactive -=- some data received
						clearTimeout( destObj.timeout );
						destObj.timeout = setTimeout("AkA.timeout('"+destId+"')",5000);
						break;
					default:
						clearTimeout( destObj.timeout );
						if( destObj.siteFun ) destObj.siteFun( false );
				}
			}
		},
		/**
		 * Construct a "request" from the supplied information, send this to the server, set a timer, store the items for
		 * processing when the data arrives or the timer expires.
		 */
	request:function( srcObj, destObj, siteUri, siteFun ) {
			var I = {
					/**
					 * Scan back to see if this element is part of a "form".
					 */
				getParentForm:function( obj ) {
						if( !obj || !obj.nodeType || !obj.parentNode ) return null;
						if( 'FORM' == obj.nodeName ) return obj;
						return I.getParentForm( obj.parentNode );
					},
					/**
					 * Get the source object from the supplied object or from the supplied "id". Use the parent
					 * "form" object if this is in a form button.
					 */
				getSrcNode:function( srcObj ) {
						// Log.message( Log.debug, 'checking [' + typeof( srcObj ) + ']' );
						switch( typeof( srcObj )) {
							case 'string':
								var srcNode = document.getElementById( srcObj );
								if( srcNode ) {
									if( !srcNode.method ) srcNode.method = 'get';
									return srcNode;
								}
								break;
							case 'object':
								// Log.message( Log.debug, 'checking object node name[' + srcObj.nodeName + ']' );
								if( 'BUTTON' == srcObj.nodeName
									|| 'INPUT' == srcObj.nodeName
									|| 'A' == srcObj.nodeName ) {
									var parentNode = I.getParentForm( srcObj );
									if( parentNode ) {
										if( !parentNode.method ) parentNode.method = 'get';
										return parentNode;
									}
								}
								if( !srcObj.method ) srcObj.method = 'get';
								return srcObj;
							default: Log.message( Log.info, 'can not go forward with source typeof[' + typeof( srcObj )
								+ '] name[' + srcObj.nodeName + '] value[' + srcObj.nodeValue + ']' );
						}
						return null;
					},
					/**
					 * Add a generated "id" to this item if it doesn't have one.
					 */
				addId:function( node ) {
						if( !node ) return;
/* */							if( !node.id ) {
							var now = new Date();
							node.id = 'R' + now.valueOf();
						}
					},
					/**
					 * Get the ID for the destination for when the content arrives.
					 */
				getDestId:function( destObj, srcNode ) {
						// Log.message( Log.debug, 'destObj typeof[' + typeof( destObj ) + ']\n srcNode typeof[' + typeof( srcNode ) + ']' );
						switch( typeof( destObj )) {
							case 'string':
								if( destObj && 0 < destObj.trim().length ) {
									var destId = document.getElementById( destObj );
									if( destId ) {
										return destObj;
									}
								}
								break;
							case 'object':
								I.addId( destObj );
								return destObj.id;
						}
						I.addId( srcNode );
						srcNode.setAttribute( 'doNotReplace', 'doNotReplace' );
						return srcNode.id;
					},
					/**
					 * If the request is for a "form" get all child nodes, otherwise just take contents from this node.
					 */
				getObjectList:function( srcNode ) {
						if( 'BUTTON' == srcNode.nodeName ) {
							var parentNode = I.getParentForm( srcNode );
							if( parentNode ) return parentNode.getElementsByTagName( '*' );
						}
						var responseList = new Array();
						responseList.push( srcNode );
						return responseList;
					},
				getPair:function( name, value, encodeIt ) {
						if( name && value ) return (encodeIt?encodeURIComponent( name ):name) + '=' + (encodeIt?encodeURIComponent( value ):value);
						return null;
					},
					/**
					 * Get the request information --- name=value pairs. Base the selection of data on the type of input. Escape the data if needed.
					 */
				getRequestPair:function( obj, encodeIt ) {
						var responsePair = '';
						outerSwitch:switch( obj.nodeName ) {
							case 'INPUT':
								switch( obj.type ) {
									case 'text':
									case 'password':
									case 'hidden':
										responsePair = I.getPair( obj.name, obj.value, encodeIt );
										break outerSwitch;
									case 'checkbox':
									case 'radio':
										if( obj.checked ) {
											responsePair = I.getPair( obj.name, obj.value, encodeIt );
										}
										break outerSwitch;
									case 'submit':
										responsePair = I.getPair( obj.name, obj.name, encodeIt );
										break outerSwitch;
									case 'file':
									case 'reset': break outerSwitch;
								}
								break;
							case 'TEXTAREA':
								responsePair = I.getPair( obj.name, obj.value, encodeIt );
								break;
							case 'SELECT':
								var opts = obj.getElementsByTagName( 'option' );
								for( var opt in opts ) {
									if( opts[opt].selected ) {
										var newPair = I.getPair( obj.name, obj.value, encodeIt );
										if( newPair ) responsePair += newPair + '&';
									}
								} // select must have at least one option
								responsePair = responsePair.slice( 0, responsePair.length-1 );
								break;
							case 'BUTTON':
								responsePair = I.getPair( obj.name, obj.value, encodeIt );
								break;
						}
						return responsePair;
					},
					/**
					 * Get the parameters for all the items.
					 */
				getParamItems:function( objectList, separator, escapeIt, destId ) {
					// Log.message( Log.debug, '=========getParamItems[' + objectList + ']' );
						var responseItem = '';
						for( var i=0; i<objectList.length; ++i  ) {
							if( 1 != objectList[i].nodeType ) continue;
							if( 'FORM' == objectList[i].nodeName ) {

								var formNodes = objectList[i].getElementsByTagName( '*' );
								responseItem += I.getParamItems( formNodes, separator, escapeIt, destId );
							} else {
								var addItem = I.getRequestPair( objectList[i], escapeIt );
								if( addItem )
									if( 1 < addItem.length ) responseItem += addItem + separator;
							}
						}
						return responseItem;
					},
					/**
					 * Get the request information, with items separated for "get" or "post" operations.
					 */
				getRequest:function( srcNode, destId ) {
						var objectList = I.getObjectList( srcNode );
						var requestItem = null;
						switch( srcNode.method ) {
							case 'post':
								requestItem = I.getParamItems( objectList, '&', false, destId );
								break;
							default:
								requestItem = '?' + I.getParamItems( objectList, '&', true, destId );
								break;
						}
						return requestItem + 'destId=' + destId;
					},
					/**
					 * Get the page to hit.
					 */
				getAction:function( srcNode, siteUri ) {
						var actionUri = null;
						if( siteUri && 3 < siteUri.length ) actionUri = siteUri;
						else {
							if( srcNode.action ) actionUri = srcNode.action;
							else if( srcNode.href ) actionUri = srcNode.href;
							else {
								var checkNode = I.getParentForm( srcNode );
								if( checkNode && checkNode.action ) actionUri = checkNode.action;
								else {
									actionUri = location.host;
									var lastSolidus = actionUri.lastIndexOf( '//' ); // extreme
									if( -1 != lastSolidus ) actionUri = actionUri.substr( 1+lastSolidus );
								}
							}
						}
						return actionUri;
					},
					/**
					 * Get the http request object. Do the micro$oft ones first, because IE7 pretends to understand the XMLHttpRequest object.
					 */
				getHttpRequestObject:function() {
						try{return new XMLHttpRequest();}catch(e){Log.message( Log.info, 'failed to get XMLHttpRequest object' );}
						try{return new ActiveXObject("Msxml2.XMLHTTP.4.0");}catch(e){Log.message( Log.info, 'failed to get Msxml2.XMLHTTP.4.0 object' );}
						try{return new ActiveXObject("Msxml2.XMLHTTP");}catch(e){Log.message( Log.info, 'failed to get Msxml2.XMLHTTP object' );}
						Log.message( Log.warn, "Can't do AJAX on your user-agent. Please upgrade." );
						return false;
					},
					/**
					 * Piece it all together. Presently only handles "get" and "post" operations.
					 */
				startRequest:function( srcObj, destObj, siteUri, siteFun ) {
						Log.logLevel = Log.off;
						var srcNode = I.getSrcNode( srcObj );
						// Log.message( Log.info, 'srcNode[' + srcNode + ']' );
						var destId = I.getDestId( destObj, srcNode );
						// Log.message( Log.info, 'destId[' + destId + ']' );
						var requestType = srcNode.method;
						// Log.message( Log.info, 'requestType[' + requestType + ']' );
						var requestUri = I.getAction( srcNode, siteUri );
						// Log.message( Log.info, 'requestUri[' + requestUri + ']' );
						var request = I.getRequest( srcNode, destId );
						// Log.message( Log.info, 'request[' + request + ']' );
						var xmlHttp = I.getHttpRequestObject();
						if( xmlHttp ) {
							try {
								destNode = document.getElementById( destId );
								destNode.siteFun = siteFun;
								destNode.xmlHttp = xmlHttp;
								destNode.timeout = setTimeout("AkA.timeout('"+destId+"')",5000);
								xmlHttp.onreadystatechange = function() {
									AkA.asyncResponse( destId );
								}
								if( 'get' == requestType ) {
									requestUri += request;
								}
								// Log.message( Log.info, 'sending type[' + requestType + '] uri[' + requestUri + ']' );
								xmlHttp.open( requestType, requestUri, true ); // add username,password
								var content = null;
								if( 'post' == requestType ) {
									content = request;
									xmlHttp.setRequestHeader( 'Content-type', 'application/x-www-form-urlencoded' );
									xmlHttp.setRequestHeader( 'Content-length', content.length );
									xmlHttp.setRequestHeader( 'Connection', 'close' );
									xmlHttp.setRequestHeader( 'User-Agent', 'XmlHttp' );
								}
								AkA.raiseWorking();
								xmlHttp.send( content );
								// could check to see if the readystatechange already == 4 and return now
								return false;
							} catch( e ) {
								Log.message( Log.debug, 'exception[' + e.message + ']' );
							}
						}
						return true;
					}
			};
//		alert( 'srcObj[' + srcObj + '] destObj[' + destObj + '] uri[' + siteUri + ']' );
		return I.startRequest( srcObj, destObj, siteUri, siteFun );
	}
};
// end of file
