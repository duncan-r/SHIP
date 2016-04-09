
SHIP
====

SHIP (Simple Hydaulic model Interface for Python) is an API for interacting
with 1D and 2D hydrulic models; principally ISIS/FMP and TUFLOW. A range
of interfaces are provided to make accessing and updating model files with
Python simple.

An overview of the main packages included in the library is available below.
For more information containing an overview of the setup of the library,
some usage examples and complete API docs build the Sphynx documentation 
provided in the docs folder.

Building the library
--------------------

A setup.py is provided so that you can build the library locally. To do this
download the libary and run the setup.py file using SetupTools.  
To build the library for installation on your maching use:  
c:\python27\python.exe setup.py sdist
To build it in .egg format for importing use:  
c:\python27\python.exe setup.py bdist_egg

Installing
----------

Once you have compiled the library you can either install it or add it to 
your script by:  
Install using Pip:  
pip install TMacTools-X.X.dev0.zip  
Append to top of Python script:  
::
	import sys  
	sys.path.append("TMacTools-X.X.dev0-py2.7.egg")



Usage
======

>>> import ship
>>> print ship.help()



List of main packages
======================

ship package:

isis - Contains modules for reading, writing and maniplating ISIS and Flood
       Modeller Pro files. Including .dat, .ief, .ief file types. 

tuflow - Contains modules reading, writing, and manipulating TUFLOW files.
         Constructs a TuflowModel object based around a given input path, such
         as a .tcf file.
         Sub modules are available in the data_files package for reading the
         contents of files that contain additional data, such as Materials and
         Boundary Condition files.

utils - Contains utility modules with file loaders, top level classes used by
        all modules - like PathHolder - and file other useful functionality
        that is used globally.
        There is also a sub package called tools that contains standalone tools
        or scripts that may be used by clients of the library to complete 
        common analysis undertaken on ISIS and TUFLOW models.
      





