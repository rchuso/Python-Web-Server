
class AkA {
	constructor( targetClass ) {
		this.targetC = targetClass;
		this.runningIndex = 0
	}
	getNextId() {
		this.runningIndex += 1
		return 'AkA_' +this.runningIndex
	}
	loadHandlerHere( item, onclick, href, destId ) {
		if( destId == null ) {
			destId = this.getNextId()
			item.setAttribute( 'id', destId )
		}
		console.log( 'loadHandlerHere add link here [' +item + '] onclick:[' +onclick + '] href:[' +href +'] destId:[' +destId +']')
//		onclickFunction = onclick
		if( onclick != null ) { onclick = onclick.slice(0,-2) }
		item.setAttribute( 'onclick', 'AkALink( "'+href+'", "'+destId+'", '+onclick +')' )
	}
	getHandlerRequest( item, attName ) {
		//console.log( 'getHandlerRequest item:' +item +' targetClass:' +this.targetC +' attName:' +attName )
		let response = null
		if( item.hasAttributes()) {
			for( var i=0; i<item.attributes.length; ++i ){
			    var att = item.attributes[i];
			    if( attName == att.nodeName ) {
			    	response = att.nodeValue
			    	break
			    }
			}
		}
		return response
	}
	loadHandlers() {
		var list = document.getElementsByClassName( this.targetC );
		let i = list.length
		while( i-- ) {
			var onclick = this.getHandlerRequest( list[i], 'onclick' )
			var href = this.getHandlerRequest( list[i], 'href' )
			var id = this.getHandlerRequest( list[i], 'id' )
			var dest = this.getHandlerRequest( list[i], 'dest' )
			list[i].removeAttribute( 'href' )
			list[i].removeAttribute( 'dest' )
			if( href != null ) {
				var destId = dest != null? dest : id
				this.loadHandlerHere( list[i], onclick, href, destId )
			}
		}
	}
}

function AkALink( href, id, onclick ) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		console.log( 'AkALink onreadystatechange readyState:[' +this.readyState  +']' )
		if( this.readyState == 4 && this.status == 200 ) {
			console.log( 'AkALink this.responseText:[' +this.responseText  +']' )
			responseObj = JSON.parse( this.responseText )
			console.log( 'AkALink responseObj:[' +responseObj  +']' )
			console.log( 'AkALink might call this function:[' +onclick  +']' )
			if( onclick == null ) {
				console.log( 'AkALink setting this text:[' +responseObj['response']  +']' )
				document.getElementById( id ).innerHTML = responseObj['response']
			} else {
				console.log( 'AkALink calling this function:[' +onclick  +']' )
				onclick( href, id, responseObj )
			}
		}
	};
	xhttp.open( 'GET', href, true );
	xhttp.send();
}

window.addEventListener( "load", loadEventHandlers );
function loadEventHandlers() {
	let a = new AkA( 'loadAkA' )
	a.loadHandlers()
}

