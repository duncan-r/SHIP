Overview
========

Main Structure
##############

The API currently has two core components:
	1. ISIS tools.
	2. TUFLOW tools.

These are used to perform various common tasks:
	1. Read files into memory.
	2. Update, copy or amend those files.
		a. Provides functions to update or change parts of those files.
	3. Write file back to disc in a format required by the models.
	4. A growing number of util classes to undertake:
		a. Common analysis on the data.
		b. Extract subsets of the data and data structures.
		
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

Logging
########

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

The logger should be requested at the top of every module using:
::
    from utils Import log
    logger = log.setup_custom_logger(__name__)

Using logging in this way means that there won’t be print statements littered 
throughout the code and it’s easy to change the output formatting, logging level 
etc in the master log file in utils.log, which will have a global effect.

API Architecture
################

This section provides further detail on the design of the API for specific components. 

Utils package
*************

There is a utils package that contains several modules with utility functions that 
are likely to be needed by most of the components of the API:
	* fileloaders subpackage. I’m still not sure if these should go here or in 
		the packages respective to the different API components (e.g. isis). It 
		does seem sensible to me to have all the loaders in the same place for 
		convenience, but maybe not:
			* DatLoader
			* IefLoader
			* TuflowLoader  
		The fileloaders package also contains two other modules:  
			* Loader
			* FileLoader  
		The loader module is a base class that should be inherited by all file loaders
		in the package. It contains some convenience methods, but also defines the 
		API to be used. The FileLoader module is the only module that you actually
		need to call to load a file. It is a factory that will call the correct type
		of file loader to use based on the file extension provided.
	* FileTools.py. Contains tools for reading and writing to files. Also contains 
		the PathHolder class that should be used by all objects that contain a file 
		path. This provides methods for storing and updating different components of 
		a file path. There are several functions in the module that make it easier to 
		update paths and catch edge cases.
	* Log.py. The logging configuration file for the API.
	* UniversalUtilityFunctions.py a collection of commonly used functions that 
		are useful to have in one place for convenience. E.g. converting a list to 
		a string. Checking that a value is a number or a string, checking that a file 
		is of a certain type based on extension, etc. 
	
Dat File
********

	A .dat file can be loaded by creating an instance of FileLoader class and 
	calling loadFile(filepath). It will:
		* Create an IsisUnitFactory object for creating the isis unit objects 
			(AIsisUnit derived classes). 
		* When DatLoader identifies a line in the file associated to a class using 
			the dictionary in the IsisUnitFactory it passes the file reading over to 
			the IsisUnitFactory to load the file according to the unit specific variables 
			(see IsisUnitFactory and RiverUnit for a better explanation).
		* When the unit has been read in it will be returned to the DatLoader class 
			and stored in the UnitCollection class. This contains convenience methods 
			for accessing the data in the different AIsisUnit derived classes.
		* Create a PathHolder object under the self.path_holder variable to store the 
			file path to the .dat file in.
		* Once the file has been read the DatLoader will return the UnitCollection 
			object to the calling class (or raise an exception).

	The UnitCollection contains a list of all the units that inherit from AIsisUnit 
	and were built by the IsisUnitFactory during the .dat file load.
	The AIsisUnit derived classes fall into two types signified by the variable 
	“self.has_rows”. If the unit has data rows, such as the RiverUnit’s channel 
	geometry this is set to True. If not then it’s set to False. This is because 
	the data for the units is split into “head_data” and “row_data”.
		
	When unit classes are created they must override two methods:
	::
		readUnitData(unit_data)
		getUnitData() # returns out_data (a list of the units data formatted for 
				# printing the .dat file with each line in a different element.
		
	These methods must implement unit specific behaviour for loading and printing 
	the unit data.

	The head_data is a dictionary containing each of the unit global variables, 
	such as comments, labels, etc.
	
	The row_data is a RowDataObjectCollection which contains a list of all the 
	ADataObject derived classes. It also contains convenience methods for 
	accessing and updating the ADataObject’s, such as adding values, adding rows, 
	getting rows formatted for printing and getting individual ADataObjects. 
	
	The ADataObjects are, currently, of 5 types:
	1.	FloatDataObject.
			For floating point values in unit data rows
	2.	IntDataObject
			For Integer values in unit data rows
	3.	StringDataObject.
			For text values in unit data rows.
	4.	ConstantDataObject.
			For unit data row values that can be one of several constants.
			This includes things such as bankmarkers which can only be “Left”, “Right” or “Bed”.
	5.	SymbolDataObject.
			For unit data row values that are either off or on  and are represented 
			in the .dat file with a symbol; like panel markers.
		
	These all contain methods for adding, removing and updating values. 
	When they are instantiated they must be given formatting details so that the 
	“getPrintableValue()” method can return the value ready to be printed to the 
	.dat file. This is done with a factory method in the ADataObject module 
	called RowDataFactory().
	
	Creating a different object collection for each of the values allows simple 
	access to modifying, loading and printing them. The best initial approach to 
	looking into the AIsisUnit, UnitCollection, RowDataObjectCollection and 
	ADataRowObject and the associated factories mentioned above is to review how 
	they are implemented in the RiverUnit.
	
	Data within the ADataRowObject should be accessed using the ROW_DATA_TYPES enum
	defined in the __init__module of the datunits package.
	

IEF File
********

	An ISIS .ief file can loaded by creating an instance of FileLoader class and 
	calling loadFile(filepath). It will:
		* Load the ief file at the given path into a list.
		* Search through the list line-by-line.
		* When it reads a line corresponding to the key sections of the file, such as 
			“[ISIS Event Header]”, it will add the data to the section specific list 
			or dictionary.
		* Continue in this fashion until all parts of the file have been read.
		* Create an object of the Ief class from the loaded data.
		* Create a PathHolder object called self.path_holder to store the file path.
		* Return the Ief object.
	
	The Ief object contains methods to:
		* Obtain file paths.
		* Get and set variables.
		* Get the printable version of the ief file for writing to file (getPrintableContents())
 
TUFLOW Files
************

	A Tuflow .tcf file can be loaded by creating an instance of FileLoader class and 
	calling loadFile(filepath). This will:
		* Load the contents of the tuflow model starting from the given tuflow
			model file.
		* Create a TuflowModel object and populate it will a ATuflowModelFile and 
			ATuflowFilePart objects and reference to unique identifying hashcodes
			created during the load process.
		* The TuflowModel will then be returned by the FileLoader.
		
	The TuflowModel class provides methods for accessing all of the data in the
	model. These include convenience functions, such as:  
		* Fetching file names or checking they exist.
		* Getting list of all of the model files (tcf, tgc, etc)
		* Getting TuflowFilePart by type (GIS, DATA, MODEL, RESULT, VARIABLE)
		* Getting TuflowModelFiles, i.e. particular control files in the model.

	When greater control is required you can obtain the TuflowModelFile's from the
	TuflowModel. Particular categories can be specified (tcf, tgc, etc). These objects
	contain the TuflowFilePart's loaded from the specific file. More detail on these
	are given below. The TuflowModel allows you to:	
		* Get TuflowModelFile's by category (tcf, tgc, etc)
		* Get the TuflowFilePart corresponding to a particular TuflowModelFile.
		* Get the TuflowModelFile corresponding to a particular TuflowFilePart (MODEL type).
		
	Accessing data of certain types is done using the FILEPART_TYPES enum in the tuflow package.
	These include the following:
		* MODEL - files that contain other model data (tcf, tgc, etc)
		* DATA - files that contain links to other files.
		* GIS - gis file references.
		* VARIABLE - model variables.
		* RESULT - result, check, or log file references.
		
	The TuflowModel is made up of several key components. Which are covered in
	more depth below.
	
	
TuflowModelFile
----------------

	This is the object that stores all of the data loaded from a Tuflow control
	file. You can obtain either an individual TuflowModelFile, types of
	TuflowModelFile (tcf, tgc, etc), or all TuflowModelFile's from the TuflowModel.
	
	The TuflowModelFile's contain a list, called contents, with all of the 
	TuflowFileParts in the order that they were loaded (as well as any unknown
	contents (comments etc) but these aren't much use in general).
	
	The contents list and it's components can be accessed using the class methods
	including:  
		* Getting file names
		* Getting absolute or relative paths
		* Getting TuflowFile's
		* Getting ModelVariables
		* and more.
	
	
TuflowFilePart
--------------

	TuflowFilePart objects are used to store the contents of the Tuflow input
	files. These are the commands within the file e.g.:
	::
		! (1) Variable declaration
		GIS Format == SHP
		
		! (2) File command
		SHP Projection == ..\model\gis\Projection.prj
		
		! (3) Reference another model file command
		Geometry Control File == ..\model\mymodel_2m_geometry_v1-2.tgc
		
		! (4) Reference a file containing additional data
		BC Database == ..\bc_dbase\mymodel_v1-1.csv
    
		! (5) Call to a gis file (also uses a piped command
		Read GIS Z Line THICK == gis\mymodel_2d_zln_channel_v1-0_L.shp | gis\mymodel_2d_zln_channel_v1-0_P.shp
		
		! (6) Output folder 
		Output Folder == ..\results\2d\

	When the files are read in by the TuflowLoader they are initially assessed
	by the command that it used in order to determine which type of data they
	contain (DATA, GIS, etc) and then possibly further defined by the file extension.
	
	For example: 
		* Line (1) above will be stored under the VARIABLE type and the contents
			of the line will be stored in a ModelVariable object.
		* Line (2) will be stored under the GIS type and the contents of the 
			line will be stored in a GisFile object.
		* Line (3) will be stored under the MODEL type and will cause a 
			TuflowModelFile to be created to store data when it is read.
		* Line (4) will be stored under the DATA type and the contents of the
			line will be stored in a DataFile object.
		* Line (5) will be split into two seperate entries, one for each file path,
			and two GIS types and GisFile objects will be created. They will
			however contain references to each other for association.
		* Line (6) will be stored under the RESULT type and the line contents
			will be stored in a SomeFile object.
			
	Any sections of the model files that cannot be interpretted by the TuflowLoader
	class will be added to a list of unknown sections. These hold parts of the 
	file that are read in and stored to be written out in exactly the same way.  
	This might include comments, blank lines or commands that are not yet understood
	by the file loader.


DataFileObject
--------------

	Files that are loaded into the DATA type (and by exception a couple of GIS
	type files) are expected to contain additional data that might need to be 
	read. For example, line (4) above references a boundary condition database 
	file. Others include materials.tmf/.csv files. 
	
	This type of file can contain additional data that may need to be read or
	updated. E.g. manning's values in materials files or additional file 
	references in the boundary condition files.
	
	To avoid an unecessarily complicated TuflowModel structure and long load times
	when access to this data is not required the contents are not read during the
	normal model load. To read them the datafileloader module is used. While it is
	possible to call the specific file loader directly it is easier to use the 
	factory method. This will also make some checks to ensure files are supported.
	
	::
		from tuflow.data_files import datafileloader
		mydatafileobject = datafileloader.loadDataFile(DataFile object)
		
	This will return an instance of DataFileObject containing contents loaded
	from the file. It is then possible to interrogate the RowDataObjectCollection
	that contains the data read in.
	
	Currently the following subclasses exist:
		* BcDataObject - for boundary condition files.
		* TmfDataObject - for materials .tmf files.
		* MatCsvDataObject - for materials .csv files.
		* XsDataObject - for 1d_xs estry cross section gis files.
		
	Some of these can also contain references to other data that may be loaded,
	e.g. the MatCsvDataObject will contain references to the DatafileSubfileMat
	class containing any depth-mannings files reference in the materials file.
	
	Additional class can be constructed, but should inherit from ADataObject for
	the main data file or ADatafileSubfile for sub files. 
	
	All of these classes have associated enums as well to referencing the contained
	RowDataObjectCollection data:
		* BcEnum
		* TmfEnum
		* MatCsvEnum
		* XsEnum
		* SubfileMatEnum


Others
------

	As well as the main components there are come other classes:
		* TuflowTypes - used to store the different commands (i.e. Read GIS) 
			that are used and associate them to different types (i.e. GIS).
		* ModelOrder - A graph used to store the tuflow files as they are read
			and maintain the order that they are read in.
			
	Unless you are dealing with low level reading in or writing out of the model 
	files these are not used.
	
