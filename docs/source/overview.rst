.. _overview-top:

********
Overview
********

The SHIP library can be used to read, write and amend the majority of Flood
Modeller Pro and Tuflow model configuration files. If you find that there is a
particular file type that you need which isn't supported, please make a feature
request (or even consider :ref:`contributing`).


The API currently has three core packages:

   - **fmp**: containing all Flood Modeller interfaces.
   - **tuflow**: containing all of the Tuflow interfaces.
   - **utils**: containing a range of utilities that are shared throughout the rest
     of the library.

******
Topics
******

*These docs are currently in the process of being put together. There are*
*probably a lot of things missing and I'm sure some (many?) mistakes. If you*
*find anything wrong or unintelligible please let me know.*

The :ref:`overview-intro` on this page covers the basics of loading and 
accesssing the data in both Flood Modeller and Tuflow models. You'll want to 
start here and when you've got your head around this look at the Flood Modeller 
and Tuflow specific sections below for more details.


Flood Modeller
==============

   - :ref:`ief-top`: class that contains all of the .ief file data.  
   - :ref:`DatCollection-top`: class that contains all of the .dat and .ief file data.  
   - :ref:`unit-top`: class' representing all of the different components of a
     Flood Modeller .dat or .ied file.  
   - :ref:`rowdatacollection-top`: class containing all of the variable length 
     data in AUnit types.
   - :ref:`unitdescriptions-top`: Summary of all of the currently supported units
     in the API and their head_data and row_data keys.

Tuflow
======

   - :ref:`tuflowmodel-top`: container class for a loaded tuflow model.
   - :ref:`controlfile-top`: container class for all parts from a type of control
     file.
   - :ref:`tuflowpart-top`: main data store for sections of tuflow control files.
   - :ref:`addingtuflowparts-top`: overview of how to add new TuflowPart's to a
     loaded TuflowModel.
   - :ref:`addingtuflowparts-saving`: how to save changes to disk.

Other
=====

   - :ref:`pathholder-top`: class for storing data pertaining to filepaths.


.. _overview-intro:

************
Introduction
************


##############
Loading models
##############

All the file loader modules can be found in the ship.utils.fileloaders package. 
The only interface you need to use for loading all model files is the FileLoader class::
   
   # Import the FileLoader class
   from ship.utils.fileloader.fileloader import FileLoader
   
   dat_path = "c:/path/to/an/fmp/datafile.dat"     # Fmp .dat model file
   tcf_path = "c:/path/to/an/fmp/tuflowfile.tcf"   # Tuflow .tcf file
   ief_path = "c:/path/to/an/fmp/ieffile.ief"      # Fmp .ief run file
   ied_path = "c:/path/to/an/fmp/iedfile.ied"      # Fmp .ied boundary file
   
   # Get the loader and use it to load the .dat file.
   # This returns a loaded FMP model as a DatCollection object.
   loader = FileLoader()
   fmp_model = loader.loadFile(dat_path)
   
   # This same loader can be used for any type of file.
   
   # Get the loaded tuflow model as a TuflowModel object
   tuflow_model = loader.loadFile(tcf_path)
   
   # Get the loaded .ief file as an Ief object
   ief = loader.loadFile(ief_path)
   
   # ... etc


####################
Accessing model data
####################

Now that you have a loaded model/model file you can access the data that it 
contains. The approach to this varies slightly depending on which kind of 
model or file type was loaded.


Flood Modeller
==============

The main class used for interacting with Flood Modeller models is the 
DatCollection class. This is an iterator based class that contains all of the
data in the either .dat or .ied files (depending on which was loaded).

This class contains several interfaces for accessing and updating data within
the model. The model data is contained within the 'AUnit' type classes 
(e.g. RiverUnit, BridgeUnit, RefhUnit). These can be accessed by iterating 
through the DatCollection or they can be grouped::

   # ... We have a DatCollection, loaded as above
   dat = loader.loadModel(dat_path)
   
   # You can loop through all of the Units in the model
   for unit in DatCollection:
      print (unit.name)       # The main label for the unit.
      print (unit.unit_type)  # Would be 'Arch' for a BridgeUnitArch
      
   # Or you can retrieve a subset of units in a variety of ways
   # By category. Returns a list
   bridges = dat.unitsByCategory('bridge')
   
   # By type. Returns a list
   bridges = dat.unitsByType('arch')
   
   # By name. Returns a single instance
   bridge = dat.unit('SECT3_BU')

Once you've accessed a unit or a set of units you can read and interact with
the data they contain. The setup of the unit classes tries to remain relatively
true to that in the FMP software to ease the learning curve. There are two main 
types of data in FMP units: 'head_data' and 'row_data'. 

In keeping with the bridge example above:

   - head_data (dict): 
       single variables used by a unit type (e.g. comment, remote_us,
       calibration_coef, etc). The naming scheme tries to remain close to those
       used in the software and the help manual, although these two vary at times!
   - row_data (dict): 
       variable number of data entries, like geometry data in 
       a lot of units, and bridge opening data in bridges. All row_data have a
       'main' key, the main row data - usually geometry. The dict values are
       RowDataCollection objects.

For a summary of the head_data keys, row_data keys, and the unit type and
category strings see :ref:`unitdescriptions-top`.

Accessing head_data is simple::

   # You could loop through a list of return type/category as you would with
   # any list, but for this example we'll use a single unit.
   
   # As above - note that you don't have to provide a type or category, but if
   # you don't you may get the wrong unit. For example: a river and adjacent
   # Refh unit can have the same name.
   bridge = dat.unit('SECT3_BU', 'bridge')
   
   # Print upstream label, downstream label, category and type
   print (bridge.name, bridge.name_ds, bridge.unit_category, bridge.unit_type)
   
   # Access items in the head_data
   remote_us = bridge.head_data['remote_us'].value
   coef = bridge.head_data['calibration_coef'].value
   
   # updating it is the same
   bridge.head_data['remote_us'].value = 'diff_sect'
   
Accessing the row_data is a little more involved, but not too complex either.
There's two main things you need to know:
   - All the data is held in a RowDataCollection object. This stores the entries
     for a particular data row (e.g. for a BridgeUnit 'main' row_data entry 
     this would contain values for chainage, elevation, manning's, embankments).
   - RowDataCollection's store this data in DataObject classes. These group the
     same types of data into a single object (e.g. all the chainage, or elevation).

**Note**
*There are two functions in the AUnit itself that you can use as convenience*
*functions for accessing RowDataCollection data*::

   from ship.fmp.datunits import ROW_DATA_TYPES as rdt

   # Get a DataObject containing the CHAINAGE data
   dobj = bridge.rowDataObject(rdt.CHAINAGE, rowdata_type='main')
   
   # Get a specific row as a dict. Keys are ROW_DATA_TYPES and values are for
   # a specific row index
   row = bridge.row(0, rowdata_key='main')
       
If you want to access rows of data there are two functions that you will probably
want to use either:

   - **rowAsList(index)**: return a list of that data in the row at index where the
   - **rowAsDict(index)**: return a dict of that data in the row at index where the
     keys are ROW_DATA_TYPES (in datunits.__init__.py module).
   - **iterateRow()**: returns a generator that can be used to loop all rows.

Example::

   # list
   row = bridge.row_data['main'].rowAsList()
   # dict
   row = bridge.row_data['main'].rowAsDict()

   # Loop the row_data
   for row in bridge.row_data['main'].iterateRows():
      print (row) # prints a list
   
   # You can also get all the row data if you want
   rows = bridge.row_data['main'].toList()   # Returns list of lists with all data
   rows = bridge.row_data['main'].toDict()   # Returns dict of lists with all data


Most of the time you will probably want to access the different DataObjects
(defined by ROW_DATA_TYPES constants) held by the collection. If you only need 
to read the data the best approach is to use either:
   
   - **dataObject(ROW_DATA_TYPES)**: return a DataObject.
   - **dataObjectAsList(ROW_DATA_TYPES)**: return a list of the data in the DataObject. 
   - **toDict()**: returns a dict of all of the DataObject with values in a list
     and keys as ROW_DATA_TYPES.

Note that you can also get these from the AUnit itself with:

   - dataObject(ROW_DATA_TYPES, rowdata_key='main')
   - dataObjectAsList(ROW_DATA_TYPES, rowdata_key='main')

Example::

   # Import the ROW_DATA_TYPES enum
   from ship.fmp.datunits import ROW_DATA_TYPES as rdt

   # Get a list of a specific type
   elevations = bridge.row_data['main'].rowAsList(rdt.ELEVATION)
   
   # Get a dict of all types. Returns a dict where keys are the ROW_DATA_TYPES
   # and the values are lists of all values in that type
   row_stuff = bridge.row_data['main'].toDict()
   
   # First elevation entry and first roughness entry:
   elev1 = row_stuff[rdt.ELEVATION][0]
   rgh1 = row_stuff[rdt.ROUGHNESS][0]
  
If you want to update the values in a DataObject or you need more control you 
you should use the DataObject itself::

   rgh_obj = bridge.row_data['main'].dataObject(rdt.ROUGHNESS)
   
   # You can now loop through data_obj and read or update each entry
   for r in rgh_obj:
      print (r.getValue)
      
      # Note that rgh_obj returned above is a shallow copy so changes you make
      # here will also be made in the DatCollection.
      r.setValue(r.getValue * 1.2)

**NOTE**
*The above approach is fine if you just want to update some values, like* 
*altering the roughness above. DON'T use this to add or remove values from the*
*DataObject! RowDataCollection keeps track of the length of the different*
*DataObjects and will start throwing errors if they differ.*

You can check to see if a unit has any row_data with::

   # prints True for bridge units (False for, say, an OrificeUnit)
   print (bridge.has_row_data)
   
The primary RowDataCollection (row_data) is always called 'main'. Although this
may seema little confusing it's fairly easy to tell what the main collection is
and it helps not having to remember lots of different key names for a common
task.
Other row_data key's are specific to what they do. For example with a
UsbprBridge::
   
   culver_rows = usbpr.row_data['culvert'] # bridge culvert data
   opening_rows = usbpr.row_data['opening'] # bridge opening data
   
That's the end of this short introduction on the fmp package. There's obviously
a lot more you can do; we haven't covered reading .ief files yet and we haven't
really looked at updating or adding new content. For the .ief files you will
want to have a look at :ref:`Ief-top` and for more on dealing with .dat files and
.ied files :ref:`DatCollection-top`. You can also find more information
on :ref:`rowdatacollection-top` here.

   
Tuflow
======

Similar to the DatCollection in the fmp package, the tuflow package has a class
called TuflowModel. This is the main interface for all data in a tuflow model::

   tuflow = loader.loadFile(tcf_path)  # returns TuflowModel instance 
   
   # A couple of convenience methods:
   # Get file paths
   fpaths = tuflow.filePaths()
   
   # update the model root
   tuflow.root = 'c:\new\model\directory

The TuflowModel object itself doesn't actually do a lot. It has a few
convenience functions, but it's mainly just a container for the ControlFile
objects. Most of your interactions with a tuflow model will be through the
ControlFile interface. 

There is one ControlFile for each of the different tuflow control file types.
They are held in a dict in TuflowModel.control_files and can be referenced 
using the following keys: 'TCF', 'ECF', 'TGC', 'TBC', 'TEF'::

   # Get the 'TGC' control file. Contains all of the .tgc type files and their 
   # contents.
   tgc = tuflow.control_files['TGC']

ControlFile objects contain two main collections, a collection of 'parts' in a 
PartHolder class and a collection of 'logic' in a LogicHolder class. Almost all
of the content in a TuflowModel is held in these iterators.

The core data structure of a tuflow model is the TuflowPart - the objects held 
in the PartHolder collection. TuflowPart is abstract, but it is inherited by 
all other components of a Tuflow model: including logic. Similar to the way 
that all units are subclasses of AUnit in the fmp package. Generally they are 
further subclasses from three different interfaces:

   - **ATuflowVariable** - all of the variables in a tuflow model, commands like
     'Set IWL == 12' for example.
   - **TuflowFile** - all of the files in a tuflow model, command like
     'Read GIS Z Line == ..\gis\somefile.shp'
   - **TuflowLogic** - all logic contructs in a tuflow model. If-else and define
     logic is stored in these.
     
Of the three interfaces above the TuflowLogic is a little bit different as it is
more of a container for other items. The other two store data related to a 
specific line in the file.

The most common type of variable class you'll see are:

   - **TuflowVariable**: standard variable class used for most variables in the
     tuflow model files.
   - **TuflowKeyVal**: used where a placeholder and variable are supplied at the 
     same time, for example 'BC Event Source == Q100 | SHIP'.
   - **TuflowUserVariable**: user defined variables. for example 
     'Set Variable MyTcfVariable == 1'
     
The most common types of file class you'll see are:

   - **TuflowFile**: this is the standard file class. Usually things will be further
     refined than this, but it does get used sometimes.
   - **GisFile**: stores all GIS type files.
   - **ModelFile**: stores all tuflow control file commands, for example the command
     'Read Geometry File == '..\model\mygeomfile.tgc'
   - **DataFile**: stores all commands that contain files with additional information
     such as 'BC Database' or 'Read Materials File' commands.
   - **ResultsFile**: any command the deals with output, like 'Output Folder =='
     or 'Write Check Files ==' or 'Log Folder =='.


Now we have an idea of the basic structure of the tuflow package we can try and
access some data::

   tuflow = loader.loadFile(tcf_path)  # returns TuflowModel instance 
   
   # You can loop through the control_files dict and do everything if you need.
   # Here, to save typing, we'll just use the TGC ControlFile
   tgc = tuflow.control_files['TGC']
   
   # You can then loop through all of the TuflowParts if you need
   for part in tcg.parts:
      # Prints out type like 'variable', 'model', 'gis', 'result', etcx
      print (part.obj_type)

   # Or you could access subsets of the collection
   
   # This will give you all ATuflowVariable parts in the TGC file.
   variables = tgc.variables()   # Returns a list of ATuflowVariable types
   
   # This will give you only the gis files in the TGC file.
   # To do this you'll need to import the FILEPART_TYPES enum from tuflow.__init__.py
   from ship.tuflow import FILEPART_TYPES as ft
   gis = tgc.files(part_type=ft.GIS)   # Returns a list of GisFile types
   
   # You can loop through the returned lists to access the data in the TuflowPart
   for v in variables:
      print (v.value, v.command)
   
   for g in gis:
      print (g.filename, g.command)

There is also a really useful method in ControlFile for querying the
TuflowPart's that contain certain strings: the contains() method. This takes
several kwargs:

   - **command(str)**: text to search for in a TuflowPart.command.
   - **variable(str)**: characters to search for in a TuflowPart.variable.
   - **filename(str)**: text to search for in a TuflowPart.filename.
   - **parent_filename(str)**: text to search for in a 
       TuflowPart.associates.parent.filename.
   - **active_only(bool)**: if True only parts currently set to 'active' will
       be returned. Default is True.
   - **exact(bool)**: Default is False. If set to True it will only return an
       exact match, otherwise checks if the str is 'in'.

and will return a list containing all of the TuflowPart's that match the kwargs.
If multiple kwargs are given a part must match all of them to be included in 
the returned list::

   # Returns a list containing all of the 'Timestep ==' TuflowParts that have
   # a value of '2.5'.
   timesteps = tgc.contains(command='Timestep', variable='2.5')

It uses an 'in' clause to check for the variable so if you ask for '2' and there 
is another with '2.5' both will be returned. If you don't want this you can
set the 'exact' kwarg to True.

You can also access the ModelFile objects for the control files you are looking
at from the ControlFile class. That's a slightly confusing way of saying that
a ControlFile is not the contents of one .tgc, but the contents of all the
.tgc files. The command 'Read Geometry File ==' is actually in a TCF ControlFile
and you can access it from there, but can also access it from the TGC
ControlFile through the control_files list::

   # Loop through all of the ModelFile parts that were used to load the 
   # TGC ControlFile contents
   for c in tgc.control_files:
      print(c.filename)
   
TuflowParts contain reference to other objects that they have an association 
with. This is done through the 'associates' object. Currently these include:

   - parent: the ModelFile that contains the TuflowPart.
   - logic: TuflowLogic associated with this TUflowPart. This can == None.
   - sibling_next: Another TuflowPart on the same command line as this.
   - sibling_prev: Same as sibling_next except it is the TuflowPart to the
     left rather than the right.
     
Continuing with the TGC ControlFile gis list from above; these are accessed like so::

   for g in gis:
   
      # Get the parent. The parent will be a ModelFile object and will also be 
      # in the control_files list discussed above
      parent = g.associates.parent
      print (parent.filename, parent.obj_type)
      
      # Some file commands can be 'piped' together with '|' symbol. This is
      # quite common with gis commands like:
      # Read GIS BC == gis\2d_bc_hx_L.shp | gis\2d_bc_cn_L.shp
      # if g.filename is 2d_bc_hx_L we will have the following...
      
      # Prints 'No previous sibling'
      associate = g.associates.sibling_prev
      if associate is not None:
         print (associate.filename)
      else:
         print ('No previous sibling')

      # Prints '2d_bc_cn_L'
      associate = g.associates.sibling_next
      if associate is not None:
         print (associate.filename)
      else:
         print ('No next sibling')

All TuflowParts have these associates. So they are accessible whether it is a
TuflowFile type or ModelVariable type or TuflowLogic type.

**IMPORTANT**
*It's important to know that all of the TuflowPart's are mutable objects. This*
*has a lot of advantages when it comes to propogating updates through the*
*model heirachy, but with great power comes great responsibility. For example*
*if you do this*::
   
   # ...taking from the above example
   parent = g.associates.parent
   
   # change the filename of the parent
   parent.filename = 'something_else'
   
It will update the filename for the *actual* ModelFile object that the parent
references. I.e. if you were to access the parent associate of a different
TuflowPart, or any other reference, the filename will equal 'something_else'.
If you want to get a copy of the TuflowPart and change things about without 
affecting the other instances you will need to do::

   parent = g.associates.parent
   
   # Return a whole new object that's not associated with the original
   new_parent = parent.copy()
   
   # If you want to compare two TuflowParts to see if they're the same just use
   # the standard '==' operator
   if parent == new_parent:
      print ("They're equal")
   else:
      print ("They're different")   # Will print this one

Also note that you don't want to just reassign self.associates.parent = new_parent
as the new_parent will be a 'hanging object', if you like. Meaning that it 
isn't associated with a, in this case, TGC ControlFile and it isn't referenced
by a TCF or another TGC file. For more information on this have a look at the
:ref:`addingtuflowparts-top` section.

It's worth remembering that there are a few convenience methods available for
easily accessing certain types of data that are commonly needed. For example
both the TuflowModel and ControlFile classes contain a method for checking that
all of the file paths in the model exist::

   # From the TuflowModel class.
   failed = tuflow.checkPathsExist()
   
   # From the ControlFile class. Note the one above is just a loop that calls
   # this method in all of the ControlFile's
   failed = tgc.checkPathsExist()
   
   # failed is a list of TuflowFile's that couldn't be found on disk.
   # To check what the paths are you could do
   for f in failed:
      print (f.getAbsolutePath())

And the control files contain a method for efficiently getting all file path
details based on certain conditions::

   # Returns all absolute paths from GIS FILEPART_TYPES
   # If absolute == False only the file name will be returned
   paths = tgc.filepaths(filepart_type=ft.GIS, absolute=True)
   
   # By default the filepaths method won't return duplicates. If you want to
   # know when there are duplicates just set the flag to False.
   # Also note here that no filepart_type is stated. This means that the paths
   # of all TuflowFile type objects will be returned (i.e. all paths in the model).
   paths = tgc.filepaths(no_duplicates=False)

For more information on how to use :ref:`controlfile-top`'s follow the link.


Finally for this intro, here's a few notes on logic structures. Tuflow models
can contain if-else and define-something logical clauses in the control files.
These are evaluated using the scenario and event variables which can be either
set in the control files (these will be a TuflowModelVariable type) or added
to the command line call.

When loading a .tcf file with FileLoader you can pass an additional argument
that contains the scenario and event values that would normally be put at the
command line. This argument is a dict setup like so::

   se_vals = {
                'scenario': {
                   's1': 'scen1', 's2': 'scen2', 's3': 'scen3'
                 },
                'event': {
                   'e1': 'evt1', 'e2': 'evt2'
                }
             }   

You do not have to include both (or either) but the main keys must be
'scenario' and/or 'event'. Anything else will be ignored. There is a 
function in utilities for converting a string version (such as that entered
into the FMP runform (.ief). That saves you from having to convert it into a dict
yourself::

   # import the utilfunctions
   from ship.utils import utilfunctions as uf
   
   # Returns a dict formatted exactly as descibed above
   se_vals = uf.convertRunOptionsToSEDict("s1 scen1 s2 scen2 e1 evt1 e2 evt2")
   
   # You can now do this if you want
   loader = FileLoader()
   tuflow = loader.loadFile(tcf_path, se_vals)
   
If your model contains logic you may want to be able to interogate the contents
using this logic. TuflowModel objects contain a variable 'user_variables' which
is a UserVariables class. This object stores both scenario and event values and
any user defined variables (TuflowUserVariable - see above). If you call the
following method in the UserVariable class you will get the same dict discussed
above::

   se_vals = tuflow.user_variables.seValsToDict()
   
Almost all of the ControlFile class methods accept this dict as an argument. 
When given it will only return the TuflowPart/filepaths/whatever that are
compatible with those scenario and event variables (i.e. anything outside the
logic clauses, and everything within the logic clauses that match the 
scenario and event logic). Say we have the following .tgc file::

   Set Code == 0 
   Read GIS Code == gis\2d_code_shiptest_tgc_v1_R.shp 
   Read GIS Code BC == gis\2d_bc_hx_shiptest_tgc_v1_R.shp 

   ! Call another tgc file
   IF SCENARIO == scen1 | scen1more 
      if scenario == scen1more 
         Read GIS Whatevs == gis\2d_whatevs_shiptest_tgc_v1_P.shp 
      else if scenario == scen1
         Read GIS Whatevs == gis\2d_whatevs_shiptest_tgc_v2_P.shp 
      end if
      Read File == test_trd1.trd
   ELSE ! comment for else
      Read File == test_trd3.trd ! trd3
   END IF
   
And we loaded our model (or updated them later, but we'll stick to loaded 
for the time being) with the following scenario and event vals::

   se_vals = {
                'scenario': {'s1': 'scen1'},
             }
   tuflow = loader.loadFile(tcf_path, se_vals)

And we wanted to get only the file paths that fell within our current setup for
scenario (and event) variables, i.e. where the scenario == scen1::

   tgc = tuflow.control_files['TGC']
   se_vals = tuflow.user_variables.seValsToDict()
   
   paths = tgc.filepaths(se_vals=se_vals)
   print (paths)
   
   # Would print the following
   ['2d_code_shiptest_tgc_v1_R.shp',
    '2d_bc_hx_shiptest_tgc_v1_R.shp',
    '2d_whatevs_shiptest_tgc_v2_P.shp',
    'test_trd1.trd']

**NOTE**
The checks for scenario and event logic are recursive. They will search all the
way up through the parent heirachy to make sure they should be included. This
means that if you have, for example, two .tgc. files within a logic clause and
only one is active, then all TuflowParts that lead back to the .tcg ModelFile
that is not in the correct logic clause will be ignored. So don't be surprised
if a TuflowPart that doesn't have any logic associate is skipped. If you follow
it back up the heirachy you will (hopefully) find that it's the correct
behviour.
   
   
   
   