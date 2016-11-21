.. _feature-requests:

****************
Feature Requests
****************

All feature requests are considered. So please feel free to offer any that you
have. However, please be aware that this library is generally maintained to 
help reduce that amount of repetative code that we write for our software.
Therefore things are normally prioritised based on what we need at the time.
If you would like to :ref:`contributing` something you have added please do
so. I'd recommend letting me know if you plan to work on something though, to
avoid conflicting additions.


.. _contributing:

**********
Contribute
**********

If you use (or are thinking of using) this library and believe there are some
things that you would like to add to it, please do! If you have any questions 
I'm more than happy to discuss how aspects of it work. Over time I plan to 
add some stuff on the more intricate makeup of the structure here as well.

If you plan to work on something perhaps let me know so we don't have repeated
effort, or overlapping approaches. If you'd like to contribute something, but
you don't know what I have a long list of things like I'd like to get done.


.. _contributing-stuff:

#######
Testing
#######

The API has a suite of unit tests for all of its components. These use the 
Python UnitTest Framework. Unit tests allow for the software to be fully 
checked to make sure that it operates as intended by ensuring all function 
behaviour is reviewed for a range of circumstances.

If you want to better understand the API the tests are a good place to start. 
The tests show how the functions should be working. They should also help 
to better understand some of the data structures, which can seem a bit 
complicated on the surface.

There is a folder within the library called “unittests” that contains the 
UnitTestSuite.py file. This file calls all of the individual test modules stored 
in the “maintests” package. All new functionality should have unit tests written 
and stored in this package. The UnitTestSuite.py file should then be updated to 
call the new tests.

Whenever any changes are made to the code base in the API the full suite of unit 
tests should be run to check that the changes have not broken any other part of 
the code base.

When running the tests some errors may be raised by the logger from attempts to 
add illegal values to certain data objects. As long as all the tests pass it’s fine.

#######
Logging
#######

All logging is done through the use of the Python built in logging API. “print” 
statements should not be used for debugging.

Where output is needed use: ``logger.mychosenlogginglevel(‘mydebugmessage’)``

Where mychosenlogginglevel (in order from top down) is:
	* error
	* warning
	* info
	* debug
	
Normal outputs will probably be set to info, so anything for developer only purposes 
should be set to debug. Anything the user might find helpful should be set to info 
and any problems should be set to warning or error.

.. highlight:: python
	:linenos:

The logger should be requested at the top of every module using::

    from utils Import log
    logger = log.setup_custom_logger(__name__)

Using logging in this way means that there won’t be print statements littered 
throughout the code and it’s easy to change the output formatting, logging level 
etc in the master log file in utils.log, which will have a global effect.

################
API Architecture
################

TODO