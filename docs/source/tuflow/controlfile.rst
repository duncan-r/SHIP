.. _controlfile-top:

***********
ControlFile
***********

The ControlFile class is the primary interface for interacting with data in a
loaded Tuflow model. There is a different ControlFile instantiated for each
different type of tuflow control filed loaded. This means that if multiple
.tgc files are loaded (or .trd files within a .tgc) the contents will all be
loaded into the same ControlFile.

ControlFile's can be of the following types: 'TCF', 'TGC', 'TBC', 'ECF', and 
'TEF'. However not all are guaranteed to exist, if there are not .tef files
referenced by a model a ControlFile will not be created with the 'TEF' key.

The 'TCF' ControlFile is slightly different from the others. It is a 
subclass of ControlFile called TcfControlFile. The only difference (currently)
is the inclusion of a 'main_file' variable which contains the hash code of the
main .tcf file for identification. You don't really need to worry about this
difference in general use of the API.


########
Overview
########

ControlFile contains four member variables:
   
   - **model_type(str)**: 'TCF' | 'TGC' | 'TBC' | 'ECF' | 'TEF'.
   - **parts(PartHolder)**: iterator for storing the TuflowPart's in this model_type.
   - **logic(LogicHolder)**: stores all of the TuflowLogic in this model_type.
   - **control_files(list)**: The ModelFile's that this ControlFile was loaded from.

Note that model_type is the value used as the key in TuflowModel.control_files.
The control_files list member is just a convenience more than anything else. 
For a quick lookup of which files are included in the ControlFile. All of the
TuflowPart's have a reference to their parent (the control file they were read
in from) as well. 

The two main components are parts and logic. Between them they store all of the
actual data in the loaded model. Of the two parts is by far the most used and
is worth focusing on first. The LogicHolder, while at times integral to 
internal operations and useful to see what tuflow logic is used in the model, is
often not needed. You will find that normally you want to know how it affects
a TuflowPart and there are easy way to do that.

Most of the time you won't need to access the PartHolder directly, unless
adding or removing a TuflowPart, as there are methods within the ControlFile that
provide functionality for common tasks. However it is availabel if you want
more fine-grained control over what is returned. 


##############
Accessing Data
##############

ControlFile contains a number of methods for making common selections from the
PartHolder. Usually these involve querying certain types of data. The majority
of the methods take similar arguments, which we'll cover here:

   - **filepart_type(int)**: this accepts one of the FILEPART_TYPES enum, which can
     be found in the ship.tuflow.__init__.py file. If you want to refine your
     results to, say, only GIS files you'd use FILEPART_TYPES.GIS. This can also
     be a list of FILEPART_TYPES.
   - **no_duplicates(bool)**: sometimes the same file can be references in more than
     one place in a tuflow model. When True this will not return duplicates
     entries. It's usually set to True by default.
   - **se_vals(dict)**: if you would like to restrict the results to a particular
     subset of scenario and event values. You should supply this. For more
     information see :ref:`tuflowmodel-uservariables`.

They also contain a number of kwargs:

   - **active_only(bool)**: if True is will only return the TuflowPart's with an
     'active' status set to True. Default is True.
   - **by_parent(bool)**: If True it will return a a dict with the parent TuflowPart's
     (i.e. the TuflowPart's in ControlFile.control_files) filename as key and
     lists of all the TuflowParts that have that parent as value. Default is
     False.
   - **exclude(list)**: inverse of 'filepart_type'. Any FILEPART_TYPES in this list
     will not be returned.
   - **callback_func(func)**: a callback function that will be called before adding
     any parts. If there are some additional bespoke checks that you would like
     to make you can do it here. The callback will be given a list of the 
     currently found TuflowPart's and the current TuflowPart and MUST return
     a tuple of (bool, TuflowPart) where the bool is True if it should be added
     and False otherwise.
     
Most of the data access methods in ControlFile are simply convenience functions.
You can obviously directly access the PartHolder if you would prefer. Here's a
few key type of access you might want.

Obtaining specific TuflowPart's
===============================

If you want to get hold of a subset of TuflowPart's there are three main ways:

   - **files()**: returns all of the TuflowFile types.
   - **variables()**: returns of the of ATuflowVariable types
   - **fetchPartType()**: same as the above two, but will return whatever instance
     you request. More on this below.

Fetching types of TuflowFile and ATuflowVariable. These work in essentially the
same way, they just return different types. Note all of these functions will
return a list containing subclass' of TuflowPart::

   #
   # in this example the role of the ControlFile will be played by 'tgc'.
   #
   
   # import FILEPART_TYPES
   from ship.tuflow import FILEPART_TYPES as fpt
   
   # Get all TuflowFile and ATuflowVariable parts.
   files = tgc.files()
   variables = tgc.variables()
   
   # Get only the GIS files
   gisfiles = tgc.files(filepart_type=fpt.GIS)
   
   # Get only the USER_VARIABLE types
   # (These are variables set in control files with: 'Set myvar == 6'
   uservars = tgc.variables(filepart_type=fpt.USER_VARIABLE)

Pretty simple. 


Finding TuflowPart's containing
===============================

In addition to the general filepart_type searches you can also query for 
parts that contain certain values. This is done with the contains() method.
the contains() method takes an se_vals optional argument (see below) as well
as the following kwargs:

   - **command(str)**: text to search for in a TuflowPart.command.
   - **variable(str)**: characters to search for in a TuflowPart.variable.
   - **filename(str)**: text to search for in a TuflowPart.filename.
   - **parent_filename(str)**: text to search for in a 
       TuflowPart.associates.parent.filename.
   - **active_only(bool)**: if True only parts currently set to 'active' will
       be returned. Default is True.
   - **exact(bool)**: Default is False. If set to True it will only return an
       exact match, otherwise checks if the str is 'in'.

It will return a list of all of the TuflowPart's that meet your criterial. If
any of the criterial that you provide are not met the part will not be returned.
If a TuflowPart doesn't have a value for one of the kwargs that you supply it
will be ignored (e.g. if 'variable' kwarg is given any TuflowFile parts will
not be checked, because they don't have a 'variable' member. This means that
you can search for different types at the same time.

Finding all 'zline' files with version '1-2' example::

   # tgc is a 'TGC' ControlFile
   parts = tgc.contains(command='zline', filename='1-2')
   
Finding all 'timestep' variables. Note that here we set 'exact' to True. If we
didn't any timestep with a '2' in it would be returned (e.g. '2.5')::

   parts = tgc.contains(command='timestep', variable='2', exact=True)


Filtering by Scenarios/Events
=============================

Now you will probably, at some point, want to filter the returned
values by the current status of the scenario and event values.

**Sidebar**
*When a tuflow model is loaded, everything in the control files will be loaded*
*into memory, even if you supply scenario and event values at the command line.*
*This is a design feature, in case you want to change the status of the these*
*values later on. If you want to access only the sections of the control files*
*within certain scenarios/events you will need to check they're logic associate,*
*or do the following.*

Filtering by senario and/or event is fairly simple. Most of the methods 
accept a scenario/event values dict (see :ref:`tuflowmodel-uservariables` for
info about the setup of this dict). Here's an example::

   # 'tuflow' is our loaded TuflowModel 
   
   # Get the 'TGC' ControlFile from TuflowModel
   tgc = tuflow.control_files['TGC']
   
   # Get the currently set scenario and event values from the UserVariables dict.
   se_vals = tuflow.user_variables.seValsToDict()

   # Only get the gis files that are in the currently set scenarios/events
   files = tgc.files(filepart_type=fpt.GIS, se_Vals=se_vals)
  
So, to steal from the example given in the introduction section, which for 
reference was this::

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
   
If the scenario values were currently set to 'scen1' the only files returned
from the above method call would be:

   - 2d_code_shiptest_tgc_v1_R.shp
   - 2d_bc_hx_shiptest_tgc_v1_R.shp
   - 2d_whatevs_shiptest_tgc_v2_P.shp
   - test_trd1.trd
   
This works in exactly the same way for the variables method.

On to fetchPartType. This is actually the method that does all of the work in
the other two. The other two are basically just hooks that call this. If you
would rather just use this one you can, but you can probably get whatever you
need from the others. Essentially it takes the same arguments are the other
two with the addition of the TuflowPart instance as the first arg::

   from ship.tuflow.tuflowfilepart import TuflowFile

   # This is the same method call as above
   files1 = tgc.files(filepart_type=fpt.GIS, se_Vals=se_vals)

   # This does the same thing
   files2 = self.fetchPartType(TuflowFile, filepart_type=fpt.GIS, se_vals=se_vals)
   
   # prints True
   print (files1 == files2)

There is actually one other convenience method that is quite useful when all
you is the file paths or file names: filepaths(). It takes similar arguments
to the above, with a couple of additionals::

   # Same search as that in files1 above except it will return filename strings
   # rather than TuflowFile's like above
   filenames = tgc.filepaths(filepart_type=fpt.GIS, se_vals=se_vals)
   
   # Same as above but aboslute paths returned instead of file names
   paths = tgc.filepaths.filepart_type=fpt.GIS, absolute=True, se_vals=se_vals)
   
There is an additional argument available to the filepaths() method, 'no_blanks'.
By default it is set to True. There is probably not need to change this most of
the time. It is there because in Tuflow control files the output paths (results,
checkfiles, log files, etc) can be a folder with no filename. This means that
when you search for filename's they will return an empty str ''. This is usually
not a lot of use, so it's set to ignore these by default.

filepaths() also accepts the kwarg 'user_vars'; a dict containing the user
variables to resolve with the given values. see :ref:`tuflowpart-uservariables`
for more information.


.. _controlfile-partholder:

##########
PartHolder
##########

There is a PartHolder class referenced by every ControlFile object, using the 
variable name 'parts'. It is an iterator for all of the TuflowPart's in that
ControlFile. The PartHolder stores all of the TuflowPart's in the order that 
they are read in from the control file(s). Note that if the model contains, say,
multiple .tgc (or .trd) files it will maintain the order between these files.
If we have these two files::

   # This file: tgcfile.tgc
   #... lots of tgc commands above
   
   Read GIS Z Line == gis\somefile1.shp
   Read File == tgcreadfile.trd  ! Note this is the call to the file below
   Read GIS Z Line == gis\somefile2.shp
   #... other commands below

   ########################################   

   # This file: tgcreadfile.trd
   Read GIS Z Shape == gis\anotherfile1.shp
   Read GIS Z Shape == gis\anotherfile2.shp

The PartHolder would load these file in this order:

   - somefile1.shp
   - anotherfile1.shp
   - anotherfile2.shp
   - somefile2.shp

(The ControlFile.control_files list would also contain tgcfile.tgc and
tgcreadfile.trd)   

PartHolder contains a range of methods for accessing, adding, updating and 
removing TuflowPart's. 

Adding a part
=============

To add a new TuflowPart to the PartHolder use the add() method::

   # Assume we already have a loaded TuflowModel called tuflow
   tgc = tuflow.control_files['TGC']

   # Import factory and create a new part
   from ship.tuflow.tuflowfactory import TuflowFactory:
   line = Read GIS Z Shape == gis\buildings_R.shp ! my comment
   gis = TuflowFactory.createTuflowPart(line)
   
   # Find an existing part to put it next to. In this example we assume that
   # there's a part somewhere in the file with the following contents:
   # Read GIS Z Line == gis\walls_L.shp
   # but it could be anything.
   # Take the 0 element as we know there's only one.
   existing = tgc.contains(filename='walls_L', exact=True)[0]
   
   # Add the new 'gis' part next to existing in the PartHolder.
   # addPart takes either a 'before' or 'after' kwarg. If both are given after
   # will take precedence
   tgc.parts.add(gis, after=existing)
   
   # Note that if the part you are adding already exists in the PartHolder a
   # ValueError will be raised
   tgc.parts.addPart(gis, after=existing) # This now raises a ValueError

To replace a part using replacePart::

   # Create another part to replace our other one
   line = Read GIS Z Shape == gis\buildings_v2_R.shp
   gis2 = TuflowFactory.createTuflowPart(line)
   
   # Replace gis with gis2
   # If the old part doesn't exist it will raise a ValueError
   tgc.parts.replace(gis2, gis)

Moving a part with move()::

   # Get the part that we want to move it next to
   var = tgc.contains(command='timestep', variable='2', exact=True)[0]
   
   # Move our gis2 part from above next to the var part. This takes the 'before'
   # and 'after' kwargs like add.
   tgc.parts.move(gis2, after=var)
   
Or get rid of a part completely with remove()::

   tgc.parts.remove(gis2)
   


###########
LogicHolder
###########

