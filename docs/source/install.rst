Installing the Library
======================

Using Pip:
##########

The TMacTools Library can be easily installed with pip. It is not hosted on Pip's Cheeswheel so you
need to use a slightly different approach to normal.

1. Download the latest sdist version of the library from here: <insert link> (it will be a zip file)
   and install it with:
   
   ``pip install --ignore-installed nameofversion```
   

Including an .egg file
######################

If you are planning on providing your tool to other people who may not have the library installed you
can include it as a refernce in the top of the main file and provide the .egg file.

This can be done by adding the following to the top of your ``__main__`` file:
::
	import sys
	sys.path.append("TMacTools-0.3.dev0-py2.7.egg")
