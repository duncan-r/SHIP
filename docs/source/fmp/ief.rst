.. _ief-top:

***
Ief
***

In Flood Modeller .ief files are the run forms used to pull together and run
the different components of a model. The SHIP library contains the Ief class
for dealing with these files. It allows for accessing and/or updating the
different variables and file paths within the .ief file.

###################
Loading an ief file
###################

.ief files can be loaded like all other files, with the FileLoader class::
   
   from ship.utils.fileloaders.fileloader import FileLoader
   
   ief_path = "C:/path/to/ieffile.ief"
   
   loader = FileLoader()
   ief = loader.loadFile(ief_path)

############
Ief Overview
############

The Ief object is fairly simple, mostly because .ief files themselves are 
fairly simple. Like most components of the SHIP library the Ief class tries
to keep names and setups similar to those used in Flood Modeller (If you aren't
familiar with .ief files you might want to open one up in a text editor and
have a quick look to familiarise yourself with the contents). An Ief object
contains the following main components:
   
   - **path_holder**: a PathHolder object that contains all the path variables and
     methods.
   - **event_header**: everything that falls within the '[ISIS Event Header]'
     section of the .ief file.
   - **event_details**: everything that falls within the '[ISIS Event Details]'
     section of the .ief file.
   - **ied_data**: a list of all of the ied data in the .ief file.
   - **snapshots**: a list of the the snapshot data in the .ief file.

That's it. Everything else in the Ief class is simply methods to allow easier
access and updating of these components.

Note that the Ief class stores all data (ied_data and snapshots are a little 
different and will be covered below) in dicts. The keys for these items are
always the same as the keys in the .ief file (e.g. 2D file path has the key
'2DFile' and the .dat file path has the key 'Datafile').


##############
Accessing Data
##############

All data in the Ief class is accessed through the following three methods:

   - **getIedData**: for accessing the ied data, obviously.
   - **getSnapshots**: for accessing snapshot data, obviously.
   - **getValue**: for accessing everything else.
   
For example::

   ief = loader.loadFile(ief_path)
   
   # Returns a list of all the ied data in the Ief.
   ied_data = ief.getIedData()
   
   # If we loop the list
   for ied in ied_data:
      
      # Each element in the list is a dict with the 'name' and 'file' found in 
      # the .ief file
      print ('name' + ied['name'])
      print ('file' + ied['file'])
   
   # Return a list of all of the snapshot data in the Ief.
   snapshots = ief.getSnapshots()
   
   for snapshot in snapshots:
     
      # Again each element is a dict, this time with 'time' and 'file'
      print ('time' + snapshot['time'])
      print ('file' + snapshot['file'])
   
   
   # Accessing all the other data
   tcf_file = ief.getValue('2DFile')
   dat_file = ief.getValue('Datafile')
   timestep = ief.getValue('Timestep')
   finish = ief.getValue('Finish')
   
   # ... you get the idea
   
There is actually one other method that can be really useful at times, 
getFilePaths(). This will return a dict containing all of the filepath
data in the Ief. Note that a path will be set to None if it is not currently set::

   # Returns a dict with all of the paths
   paths = ief.getFilePaths()
   
   dat_file = paths['Datafile']
   tcf_file = paths['2DFile']    # Will be None if there is no 2DFile
   
   # This will return a list of all ied paths (no name included)
   ieds = paths['ieds'] 
   
   # Same for this - no time includes
   snapshots = paths['snapshots']
   
   
#############
Updating Data
#############

Updating the data in the Ief works in pretty much the same way. There are also
three methods:

   - **addIedFile(ied_path, name='')**: for adding a new ied file.
   - **addSnapshotFile(snapshot_path, time)**: for adding a new snapshot file.
   - **setValue(key, value)**: for everything else.
   
Example::

   ief.setValue('Finish', 12.0)
   ief.setValue('2DFile', 'c:/path/to/tcffile.tcf')
   ief.addIedFile('c:/some/iedfile.ied', 'someiedname')
   
   
######
Saving
######

If you have updated the Ief object you will probably want to save your 
changes to file. If you just want to overwrite the file that you loaded you
can call the write() method::

   ief.write()
   
If you want to save your changes to a new file you have two options. You can
either update the 'filename' variable (and directory etc too) in the 
'path_holder' member of the Ief, or you can pass an absolute path to the write()
method::

   # Change the path_holder variables
   # Note that no extension is given. This is stored in path_holder.extension
   ief.path_holder.filename = 'something_else'
   
   # or just give a new path to write
   ief.write('C:/spangly/new/ieffile.ief')
   
