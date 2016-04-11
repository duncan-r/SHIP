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

Examples
--------

Some example python modules showing how to use the API and tools are included
in the examples/ folder. This is a good place to start to get an idea of how
the library can be used to interact with model files.

Building the library
--------------------

When major releases are made they will be tagged and included on the releases
page on GitHub. These release markers will include compiled .egg and .zip
distributions, as well a the documentation as it stands at that release. You
can find this under the 'Releases' tab on the GitHub repository page. The latest
release should match the current state of the master branch.

If you would prefer to get the latest version of the library you can download
or clone the develop branch and build it yourself. The develop branch is the
active development branch and may be unstable.  

If you just want to install the latest develop version using pip do:
::
	# First time install
	pip install git+https://github.com/duncan-r/SHIP.git@develop
	
	# Upgrading
	pip install --upgrade git+https://github.com/duncan-r/SHIP.git@develop

Otherwise you can download the source and use the setup.py provided. Once you 
have obtained the code you can build it with SetupTools.  

To build the library for installation on your machine use:  
::
	$ Python setup.py sdist  

To build it in .egg format for importing use:  
::
	$ Python setup.py bdist_egg
	
You can clean up the outputs and temporary files of a previous build with:
::
	$ Python setup.py clean

Tests
-----

Unit tests for the API can be run through SetupTools with:
::
	$ Python setup.py test

If all of the tests pass without issues it should output 'OK' at the end of
the test run.

Installing
----------

Once you have compiled the library you can either install it or add it to 
your script: 
 
Install using Pip:  
::
	# First time install
	pip install SHIP-X.X.dev0.zip
	
	# Upgrading
	pip install --upgrade SHIP-X.X.dev0.zip
	
Append to top of Python script:  
::
	import sys  
	sys.path.append("SHIP-X.X.dev0-py2.7.egg")

Building Docs
-------------

Sphinx documentation source has been provided in the /docs/source/ folder.
You will need to install Sphinx and it's dependencies before you are able to 
run the documentation builder. There are a lot of dependencies to the Sphinx
library, so you may want to install it in a virtual environment. You can install
Sphinx with Pip by:
::
	$ Pip install Sphinx
	 
Sphinx can be used to build the docs in a range of formats, but the setup.py
file has been configured to use HTML output. To build the HTML docs use:
::
	$ Python setup.py build_sphinx 


Usage
======

>>> import ship
>>> print ship.help()



List of main packages
======================

isis
----

Contains modules for reading, writing and maniplating ISIS and Flood 
Modeller Pro files. Including .dat, .ief, .ief file types. 

tuflow
------

Contains modules reading, writing, and manipulating TUFLOW files.
Constructs a TuflowModel object based around a given input path, such
as a .tcf file.
Sub modules are available in the data_files package for reading the
contents of files that contain additional data, such as Materials and
Boundary Condition files.

utils
-----

Contains utility modules with file loaders, top level classes used by
all modules - like PathHolder - and file other useful functionality
that is used globally.
There is also a sub package called tools that contains standalone tools
or scripts that may be used by clients of the library to complete 
common analysis undertaken on ISIS and TUFLOW models.


Credit
======

Parts of this library make use of the excellent dbfread project by
Ole Martin Bjorndalen. It is a library for accessing data in DBF database
files. You can find the project here on GitHub 
https://github.com/olemb/dbfread
