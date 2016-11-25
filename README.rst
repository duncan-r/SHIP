SHIP
====

SHIP (Simple Hydaulic model Interface for Python) is an API for interacting
with 1D and 2D hydraulic models; currently Flood Modeller and TUFLOW. A range
of interfaces are provided to make accessing and updating model files with
Python as easy as possible.

For more information containing an overview of the setup of the library,
some usage examples and complete API docs you can clone the repo and build the 
Sphynx documentation provided in the docs folder, or view it on GitHub under 
the Wiki tab.

Notice
------

This library has had a major overhaul and cleanup. The 'develop' branch is now
set to the new version. This is in-line with the 'getout clause' that was here
before stating that everything was very beta and liable to change. now this has
happened there will hopefully not be any more major breaking changes (without
a decent deprecation period). Note that this is not completely true for the
datafileloader and datafileobject modules, which still need overhauling. The
good news is the documentation is now a lot better, so it should be easier to
see what's going on.

If you need to continue using the older (0.2.5) version there is a branch
called 'release_0-2-5' available on the repo. If you want the latest version 
(0.3.0 upwards) just clone the 'develop' branch.

Here's more context from the extract in the docs:

   *From release 0.3.0-Beta there is a significant change in the strucutre of a lot*
   *of the API. While the tuflow package is most heavily affected, with a complete*
   *restructure there are a lot of changes in the fmp package too (notably changing*
   *the name from isis to fmp).*

   *While it is obviously not ideal to make such sweeping changes, the API up until*
   *this point was always in an early development stage (as noted in the READ_ME).*
   *The tuflow package had outgrown it's initial, somewhat organic, growth and*
   *was becoming very hard to maintain and find bugs in. While the changes to the*
   *fmp package are much less extreme it seemed like a good time to make a clean*
   *break and fix a lot of things that have been causing issues. Including*
   *un-pythonic naming conventions, old unused variables, etc. The final push for*
   *this was the need to update the API from Python 2.7 to Python 2.7 and 3.3+. I*
   *feel like this was probably the best time to sort all of this out.*

   *So if you've been using this library, sorry :( . I think though that you will*
   *find it much improved and it's defintiely easier to maintain and improve going*
   *forward. Not also that "the possible API break" stage is through and any*
   *functionality will be properly deprecated for a reasonable amoutn of time from*
   *now on. For more info on what's changed see ..*

Python version
--------------

While originally developed to support Python 2.7, the library has now been 
updated to support both Python 2.7+ and Python 3.3+. In order to do this it
requires the future package (installable with `pip install future`. There are no
plans to support other versions of Python, mostly because it involves a lot more
work and requires further dependencies.

Examples
--------

Some example python modules showing how to use the API and tools are included
in the 'examples' folder. This is a good place to start to get an idea of how
the library can be used to interact with model files.

Getting SHIP
------------

The easiest way to get hold of the library is by either cloning the repo or
directly installing it with Pip.

If you just want to install the latest develop version using pip do::

	# First time install
	pip install git+https://github.com/duncan-r/SHIP.git@develop
	
	# Upgrading
	pip install --upgrade git+https://github.com/duncan-r/SHIP.git@develop

For more info on installing from source and building the docs locally with
Sphinx see the installation page of the docs.


Usage
=====

Using an installed package::

   >>> import ship
   >>> print ship.help()

Adding a bulit .egg file to a script::

   # Put this at the top of the script pointing the path to the location of
   # the egg file
   import sys
   sys.path.append("ship-0.3.0.dev0-py3.5.egg")


List of main packages
=====================

fmp
---

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
