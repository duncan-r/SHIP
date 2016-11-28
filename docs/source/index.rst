.. SHIP documentation master file, created by
   sphinx-quickstart on Fri Jan 15 11:12:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SHIP API documentation!
==================================

SHIP (Simple Hydraulic model Interface for Python) is a Python library for 
interfacing with Flood Modeller Pro and Tuflow model configuration files. You
can get the code from the GitHub repo for SHIP_.

.. _SHIP: https://github.com/duncan-r/SHIP


For an introduction to using the API and interacting with model files go to
:ref:`overview-top` .

If you have any feature suggestions or bug reports please add them to the GitHub
page. We will endevour to fix major bugs as soon as possible and welcome any
suggestions for consideration. For more information on :ref:`feature-requests`
following the link.

If you are interested in contributing to the project please take a look at the
:ref:`contributing` page. 

Please note these docs are still being put together and are not complete yet.
There is also almost certainly many typos/errors and probably some issues with
the code examples. I will try and get these sorted as soon as possible once 
focused has moved away from actually get the code together.


About versions
##############

From release 0.3.0-Beta there is a significant change in the strucutre of a lot
of the API. While the tuflow package is most heavily affected, with a complete 
restructure there are a lot of changes in the fmp package too (notably changing
the name from isis to fmp).

While it is obviously not ideal to make such sweeping changes, the API up until
this point was always in an early development stage (as noted in the READ_ME).
The tuflow package had outgrown it's initial, somewhat organic, growth and
was becoming very hard to maintain and find bugs in. While the changes to the
fmp package are much less extreme it seemed like a good time to make a clean 
break and fix a lot of things that have been causing issues. Including 
un-pythonic naming conventions, old unused variables, etc. The final push for
this was the need to update the API from Python 2.7 to Python 2.7 and 3.3+. I 
feel like this was probably the best time to sort all of this out.

So if you've been using this library, sorry :( . I think though that you will
find it much improved and it's defintiely easier to maintain and improve going
forward. Not also that "the possible API break" stage is through and any
functionality will be properly deprecated for a reasonable amoutn of time from 
now on. For more info on what's changed see :ref:`updatechanges-top`.


Python version
##############

While originally developed to support Python 2.7, the library has now been 
updated to support both Python 2.7+ and Python 3.3+. In order to do this it
requires the future package (installable with `pip install future`. There are no
plans to support other versions of Python, mostly because it involves a lot more
work and requires further dependencies.


Contents:

.. toctree::
	:maxdepth: 4
	
	install
	user guide <overview>
	ship
	modules
    

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`