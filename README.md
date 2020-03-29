This is what happens when I'm bored... I start to tinker with things which are probably best left untouched.

During this lockdown, I wanted to see if I could create something to replace the Tomcat server and SiteMesh and JSP, and all in Python. This is the result.
I've been using these technologies for some web sites, but I'm not a fan of Java (yes, I'm a Sun-Certified Java Programmer) or Tomcat or Apache or JSP.


Python Web Server
=============

This application provides a simple python web server you can run which will serve multiple web sites (with no special configuration), allow the inclusion of python inline (run on the server), and do much of what is provided by page templates - automatically.

The python was written to run on python version 3.7+

The main.py is the main code that prepares the HTTPServer code and the python that handles the request is in the server.py.
When the main.py is started, it scrapes through the web sites folder for a "processes" folder.
If it finds a folder of that name, it scrapes through the python code in that folder for anything that starts with "process", and starts that running as a background process that can start a server socket or other processing that can run in the background.
Background processes can be collecting data or updating neural networks or as I've included here: simply modify the received data over the server socket.
If I was to switch to this for my server, I'd have one background process collecting the Total Electron Content information from the data sources, another process calculating the Anomaly, another process modifying the data for the training, one process for continuing the training, and another to make the forecast for display on a server - responding over a socket.
And I'm tempted to do just this.
The context can be searched online, but the gist is this: earthquake precursors are available in the anomalous free-electron field in the ionosphere at near 350 km high and in the release of radon gas from the ground (which data is not yet available for me).
These precursors indicate stresses in the ground that could be used to forecast major earthquakes.

When a request comes in to the server, the server.py code is called (methods for "do_GET", "do_POST", and "do_HEAD", and a factory returns the appropriate handler for the request.
When the handler is done with the request, the response is sent back to the client.
If the request is for HTML or JSON content, the page is scraped for "<run>" tags, and these are passed to the python for execution. Yes, this is potentially dangerous, but if I'm writing the server, the python, and the pages, I should be reasonably safe.
And this is just a demonstration of what can be accomplished.
There are examples of this in the subIndex.html under the subdirectory src/localhost/public/sub.
This was as close to JSP as I could get.

If the handler is returning HTML code, the folder that held the HTML page is checked to see if there's a "template.html" to use as the template.
The template has a "<template>" tag whose "id" will reference the appropriate tag of the page being "wrapped".
If the template has a "<template id='body'/>" tag, this will be replaced by all the content from the "<body>" of the HTML page.
There's an example of a "<template id='fred'/> tag, and there's a section in the HTML with a "<fred>" tag whose content will be migrated to the template for sending to the client.

These tags "<run>", "<template>", and "<fred>" (or whatever else a user creating a page could envision) are definitely non-standard, but the content sent to the user's client will have these replaced with the appropriate standard HTML content.
This should also work for XHTML content.

The "test.json" file is requested (repeatedly) by button clicks that are processed by some AJAX in the main "index.html" page.
Like everything else in this collection of files, I wrote my own.
The original version of my AJAX software I called AkA.js, but for reasons which I've since forgotten - that was back in 2003.
I've included the version of this file as it existed in 2008, but it's only there for those who want a laugh.

When the page is loaded, the "AkA.js" code scans through the HTML and adds the AJAX calls to whatever has the appropriate required parts: a "class" called "loadAkA" and an "href".
You could put these on a paragraph ("<p>"), if you want, and the JavaScript will add an "onclick" which could be used to replace the content of the paragraph with the response from the server when you click on the text.
If the tag (element) also has a "dest" attribute, that referenced element will be replaced with the response from the server, instead of the current tag.

There's also lots of debug print still in the code, mostly so you can see the progress of the execution.

Since I may further develop this for actual use, if you find anything wrong with what I've written, please let me know.

My apologies to those who love pep.8 ... I don't.

