.. _DatCollection-top:

*************
DatCollection
*************

DatCollection is the main class used for accessing all of the data in a 
Flood Modeller .dat file - or, despite the name, .ief file (this is because
they are basically the same file structure). When you load a .dat file or an
.ied file the FileLoader will return a DatCollection.


.. _DatCollection-loading:

#####################
Loading dat/ied files
#####################

.dat and .ief files, like all other files, can be loaded with the FileLoader 
class::
   
   from ship.utils.fileloaders.fileloader import FileLoader
   
   ied_path = "C:/path/to/iedfile.ied"
   dat_path = "C:/path/to/datfile.dat"
   
   loader = FileLoader()
   ief = loader.loadFile(ied_path)
   dat = loader.loadFile(dat_path)


########
Overview
########

The DatCollection class is a collection of all of the AUnit types loaded (or
added later) from a .dat or .ief file. It contains methods for adding and 
removing units from the collection, as well as a range of methods for accessing
the units in different ways.

The DatCollection class is also an iterator, so you can loop through the units
withint the collection the same way as a list.

Generally you will probably want to obtain a DatCollection object by
loading an existing file (:ref:`DatCollection-loading`). If you ever need to 
create new DatCollection for a .dat file you should use the initialisedDat()
classmethod. This will setup some of the required units that are needed by all
.dat files, such as HeaderUnit and InitialConditionsUnit::

   import ship.isis.datcollection
   
   # Will create a DatCollection with required units setup already
   dat = datcollection.initialisedDat("C:/path/to/write/datfile.dat")

   # If you have some units that you've already initialised or taken from
   # another collection you can pass them in as a list. The order will be
   # preserved.
   units = [RiverUnit(), BridgeUnit(), RiverUnit()]
   dat = datcollection.initialisedDat("C:/path/to/write/datfile.dat", units)


##############
Accessing Data
##############

Accessing the units in the DatCollection is done through three main methods:

   - **unit(str, unit_type)**: for accessing a particular unit in the collection.
   - **unitsBytype(unit_types)**: for getting all of a particular type of unit.
   - **unitsByCategory(unit_categorys)**: for getting all of a particular category
     of unit.

Accessing a particular unit by name::

   dat = loader.loadFile(dat_path)
   
   # assumes there's a river unit called RIV_01 in the collection
   river = dat.unit('RIV_01', 'river')
   
   # Note you don't have to provide a unit_type to the above function, but if
   # you don't it will return the first unit with that name. E.g. If there is an
   # RefhUnit called 'RIV_01' above the river unit and we do this...
   river = dat.unit('RIV_01')
   
   # Then this will print 'refh'
   print (river.unit_type)

Most of the time you will probably want to accessing a subset of units, for
example to do something to all of the RiverUnit's or BridgeUnit's. DatCollection
uses unitsByType and unitsByCategory for this::

   # All of these methods return a list

   # Returns all BridgeUnit types in the model
   bridges = dat.unitsByCategory('bridge')
   
   # Returns all BridgeUnitArch type in the model
   arch_bridges = dat.unitsByType('arch')
   
   # Note that both of these functions will also accept a list of type/category.
   # For example to return multiple unit_types do
   bridges = dat.unitsByType(['arch', 'usbpr'])
   
Finally, because the DatCollection is an iterator you can just loop through all
of the units in the collection::
   
   for unit in dat:
      # ...do something with unit here

All of these methods return a list of AUnit types (except unit() which returns 
a single AUnit). For more information on AUnit's and how to use them and access 
their data see :ref:`Unit-top`.


#####################
Adding/Removing Units
#####################

Adding a unit
=============

Units can be added to the collection with the addUnit() method. If no index is
given the unit will be added to end of the existing units::

   # Adds a new RiverUnit after all of the existing units
   dat.addUnit(RiverUnit())
   
   # Adds a new RiverUnit at a specific index
   dat.addUnit(RiverUnit(), index=4)

The addUnit() method also takes some kwargs arguments that include:

   - **ics(dict)**: initial conditions data to add for the unit. If not supplied they
     will be set as the default. 
   - **update_node_count=True(bool)**: If you don't want to update the node count
     when adding another unit. You probably never want to set this to False it's
     only hear for when loading files.

When adding a unit you may want to find the index of an existing unit so that
you place the new unit next to it. For that you can use the index() method::

   # find the existing unit and get it's index
   index = dat.index(existing_river_unit)
   
   # or just a name. unit_type is optional, but again you probably want it
   index = dat.index('RIV_01', 'river')
   
   # You can now add the unit before or after an existing unit
   dat.addUnit(RiverUnit(), index=index)  # Add it before
   dat.addUnit(RiverUnit(), index=index+1)  # Add it after


Removing a unit
===============

Units can be removed with the removeUnit() method. This takes either an AUnit
type or a str containing the name of a unit. If you provide the name of a unit 
as a str you must also provide a unit_type::

   # Both of these would work
   
   # Remove by name
   dat.removeUnit('RiV_01', 'river')

   # Get an existing unit
   river = dat.unit('RIV_01', 'river')
   # Remove the unit from the collection
   dat.removeUnit(river)

Remove unit also takes a update_node_count value, like addUnit. Again you almost
certainly don't want to change the default.


##############
Saving Changes
##############

After making changes to a DatCollection you will probably want to be able to
save them to file. The easiest way to do this is with the write() method. The
write method takes the following arguments:

   - **filepath=None(str)**: the absolute path to save the file to. If None it will
     use the current setup of path_holder.
   - **overwrite=False(bool)**: if the filepath already exists and overwrite is
     False it will raise an IOError.
     
Saving your changes is as simple as::

   # Assume we have a loaded DatCollection called dat
   
   # Below are four ways you could write to file
   
   # 1.
   # Save to the current path settings in path_holder
   # will raise an IOError if the file already exists
   dat.write()
   
   # 2.
   # Force it to overwrite an existing file if it exists
   dat.write(overwrite=True)
   
   # 3.
   # Hand in a different path to write to
   dat.write(filpath="C:/new/file/path/mydat.dat")
   
   # 4.
   # Chainge the path_holder filename and then write
   dat.path_holder.filename += "_updated"

   # You could also change the folder too if you want
   # dat.path_holder.root = "C:/my/new/folder"

   dat.write()
   
   