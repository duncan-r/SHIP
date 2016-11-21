.. _tuflowpart-top:

**********
TuflowPart
**********

The TuflowPart interface is an abstract base class that must be inherited by
all classes storing data in tuflow control files (i.e. those held by the 
:ref:`controlfile-partholder` class in :ref:`controlfile-top`).

With the exception of TuflowLogic derived classes, which are slightly different,
all TuflowPart's hold information pertaining to a single line (or part of a 
line when dealing with piped commands) in a tuflow control file.

All the actual data loaded or added is stored in TuflowPart's. There are
currently three main types of TuflowPart:
   - ATuflowVariable: for all types of variables.
   - TuflowFile: for all types of filepath.
   - TuflowLogic: for all if-else and define logic.


########
Overview
########

TuflowPart defines a few standard members and methods required by all subclasses.
These members and methods include:
   
   - **hash(uuid4)**: uuid hash code unique to every part.
   - **obj_type(str)**: subclass specific str (e.g. 'model', 'gis', 'variable', etc)
   - **tpart_type(int)**: FILEPART_TYPE value from the tuflow.__init__.py module.
   - **active(bool)**: status flag on whether the part is currently in use or not.
     This can be set to False which will have the same effect as deleting it in
     most methods.
   - **associates(AssociatedParts)**: stores a reference to associated TuflowPart's
     like parent, siblings and logic.

Currently the following subclasses of TuflowPart exist (Note that the 
TuflowLogic derived class deal with things a bit differently, so they will be 
discussed later).:

   - **UnknownPart**: stores any data (can be multiple lines) that the loader doesn't
     understand.
   - **TuflowVariable**: standard variable store. Contains most variables decalred in
     control files. Has two members for storing the variable part of the 
     command line: 'variable' and 'split_variable'. variable is the value as
     read, split_variable is a list containing the variable separated by spaces.
   - **TuflowModelVariable**: for scenario and event values when either passes in
     from the runform/batch file, or read from the control files. Note if they
     are passed in the associates.parent == None.
   - **TuflowUserVariable**: for user defined variables set in the control files
     with the 'Set myvarname == 2' style syntax.
   - **TuflowKeyValue**: for key-value variable pairs, such as: 
     'BC Event Source == varname | Q100'.
   - **TuflowFile**: standard file store. This is subclasses by all other file types.
     Also inherits from the PathHolder class.
   - **ModelFile**: used for commands that contain refernce to control files.
   - **GisFile**: used for any command that points to a gis file.
   - **ResultFile**: used for any commands that point to files/folders to write
     out to.
   - **DataFile**: used for any command that points to a file that contains other
     readable data and possible other files with additional data, like 
     BC Database, Materials.csv and Materials.tmf.

All includes variables of 'command', the section of a command line before the
'==', and 'comment', anything after a '!' on the line. The part of the line 
after the '==' is referred to by different variable names dending on the class.
In general though if it's a variable type it will have one called 'variable'.
If it is a file it will populate the PathHolder superclass with the path it
reads in and will have the standard members and functions available in there:

Main members:
   - filename
   - extension
   - root
   - relative_root

Main methods:
   - getAbsolutePath()
   - getFileName()
   - getRelativePath()

See :ref:`pathholder-top`for more information.


##############
Accessing Data
##############

When you have accessed a TuflowPart, probably through a ControlFile, you can
access the data it contains in the following way::

   # If we have any type of TuflowFile, let's assume it's called fpart
   
   # These are true of all TuflowParts
   # Any of these may == None (although most should have a parent)
   parent = fpart.associates.parent
   logic = fpart.associates.logic
   
   sibnext = fpart.associates.sibling_next
   sibprev = fpart.associates.sibling_prev
   # Normally used for piped file commands, for example this line:
   # Read GIS Z Line == afile_R.shp | afile_L.shp | afile_P.shp
   # would be put into 3 separate TuflowFile's and afile_L would have
   # sibline_prev equal to part holding afile_R and sibling_nexxt to afile_P.shp
   
   # Accessing file variables
   filename = fpath.filename
   extension = fpath.extension
   root = fpath.root
   
   # Note this one is relative directory noted in the control file, for example;
   # Read GIS Z Line == ..\gis\somefile.shp
   # the relative_root would be '..\gis\'
   rel_root = fpath.relative_root
   
   # Get difffernt filepaths
   abspath = fpath.getAbsolutePath()
   relpath = fpath.getRelativePath()
   
   # TODO
   # ... Put stuff about different functions here
   
   
   # If we have any type of TuflowVariable, let's assume it's called vpart
   # All the associates stuff will be the same

   # accessing variables
   
   # This would be the whole variable like '2' in 'Set IWL == 2' or 'h q v MB2'
   # in 'Map Output Data Types == h q v MB2'
   var = vpart.variable 
   
   # [2] in the IWL example or [h, q, v, MB2] in the second one
   svar = var.split_variable
   
For additional information see the docstrings for the class you need in the 
tuflowfilepart.py module.

###########################
Additional TuflowFile stuff
###########################

TuflowFile overrides some of the methods of the :ref:`pathholder-top` class to
account for Tuflow specific behaviour. The main ones include:

   - **all_types(list)**: some files can actually require mutliple files with 
     different extension (think mif/mid or shp/shx/dbf). This store a list of 
     those file extensions.
   - **has_own_root(str)**: most file references in Tuflow use a relative path, but
     absolute paths can be used (and are quite common with results files). If
     this is the case has_own_root will be set to True. This is so it will be
     ignored when a global root update occurs.
   - Some subclasses of TuflowFile have their own 'type' variable (model_type, 
     result_type, gis_type). This is a simple look up to help filter different
     forms. For example gis_type may be 'mi' or 'shape', result_type may be
     'output', 'check', or 'log'.

Some of the main methods that are overriden are:

   - **absolutePathAll()**: overides the absolutePath function to return the paths
     of all the types specified in all_types. Returns a list of strings.
   - **relativePathAll()**: same as absolute, but with relative path.
   - **filenameAll(extension=False)**: same as absolute, but for file names. If
     extension arg == True the file name will be returned with the extension. 


###########
TuflowLogic
###########
   
The TuflowLogic type of TuflowPart is different to the other implementations 
discussed so far. First of all it will not be added to the PartHolder in the
ControlFile, it will be added to the LogicHolder. Secondly it doesn't hold just
the information about a particular line in a control file, it stores information
about everything within the scope of a particular if-else-end or define section.

Currently there are three subclasses of TuflowLogic:

   - **IfLogic**: for if-elseif-else-endif logic. Used by scenario and event.
   - **EventLogic**: for 'Define Event' blocks.
   - **SectionLogic**: captures all the other stuff, like defining output zones.
   
EventLogic and SectionLogic are almost the same except EventLogic is checked
when looking up scenario and event logic, while SectionLogic isn't.

All of the logic classes contain the following member variables:

   - **parts(list)**: all of the TuflowParts between the opening 'clause' and
     closing clause.
   - **group_parts(list[list])**: stores the hash codes (TuflowPart.hash) of the 
     parts in a list based on which section, or clause, it is in. EventLogic
     and SectionLogic will always only have one inner list. IfLogic may have any
     number of inner lists.
   - **terms(list[list])**: terms of the if-else/define/etc statement. Note there
     can be multiple terms so this, like above, is a list of lists.
   - **commands(list)**: part of line before the terms (e.g. 'If Scenario').
   - **check_sevals(bool)**: flag for whether scenario and event values should be
     evaluated on this. This is setup in the constructor, it just states whether
     the terms should be evaluated for scenario and event values.

**IMPORTANT**
*When adding or removing TuflowParts from TuflowLogic, as described below, you* 
*shoud use the provided methods, rather than just adding and removing from the*
*part lists. The methods will ensure that other places where the TuflowPart is*
*used are kept sane when adding or removing. For example, if you remove a*
*part from a logic clause the callback function will let the ControlFile know*
*(if one is assigned - it should be) and it will move the part from it's curren*
*location in the PartHolder list to a location after the logic clause has*
*closed. This is because the PartHolder maintains the order of the components.*
For more information see :ref:`addingtuflowparts-top`.

All TuflowLogic supports the same main interfaces for accessing, adding and
removing items. Accessing parts is generally done in the following way::

   # You can obtain a TuflowLogic instance from an associates reference or
   # from the LogicHolder in ControlFile, depending on what you need. Either
   # way you will be returned the same thing.
   # Approach 1
   logic = tgc.logic[0] # say tgc is a ControlFile instance
   # or: Approach 2
   logic = part.associates.logic  ' say part is a TuflowPart instance
   
   # You can access the components directly
   for i, g in enumerate(logic.group_parts):
      # Will print a list of hash codes for the different part in each clause
      print (g)
      
      # Prints a list of terms for each group. This is the bit after the '=='
      # in, for example: If Event == evt1 | evt2 | evt3. The terms would be
      # [evt1, evt2, evt3]
      print (logic.terms[i])
      
      # This command for the clause (e.g. If Scenario, Else If Scenario,
      # If Event, Define Event, etc
      print logic.commands[i]
      
      # Any comment that appears on the command/terms line
      print logic.comments[i]
   
   # Generally you only want to know which group a particular part is in, so 
   # that you can then check the terms of the clause or something like that
   # Following approach 2 above
   logic = part.associates.logic
   
   # Check that the part does actually have logic (i.e. is inside a clause)
   if logic is not None:
   
      # Get the group index and use it to find the logic terms etc for the part
      group_index = logic.getGroup(part.hash)
      part_command = logic.commands[group_index]
      part_terms = logic.terms[group_index]
   
Adding TuflowParts to a TuflowLogic clause generally uses two functions:

   - addPart(): for adding a part to a group
   - insertPart(): for adding a part next to an existing part.
   
These work like so::
   
   # we have a new/existing/whatever TuflowPart and we want to add it to a
   # TuflowLogic object 
   # Note that if the group doesn't exist it wil raise an IndexError. If you
   # don't supply a group it will be appended to the last group.
   logic.addPart(new_part, group=1)
   
   # new _part will be added to the same group as existing_part and 
   # immediately after it in the group order.
   existing_part = apart.associates.logic
   if logic is not None:
      logic.insertPart(new_part, existing_part)
   
Removing a TuflowPart is easy::
   
   # You can either provide a TuflowPart or a TuflowPart.hash.
   
   logic = part.associates.logic
   logic.removePart(part)
   # or logic.removePart(part.hash)

   
     



   
   
   
