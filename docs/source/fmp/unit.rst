.. _unit-top:

*********
FMP Units
*********

The AUnit class is an abstact base class that all of the components of a
Flood Modeller .dat and/or .ied file are created with, e.g. RiverUnit, 
RefhUnit, BridgeUnitArch, etc. All of the contents of the :ref:`DatCollection-top` 
are classes of AUnit type.


########
Overview
########

The AUnit class defines a interface with a few variables and a number of
methods that are implemented in all of the concrete unit classes. Namely:

   - **unit_name(str)**: name of a particular unit instance, this is the
     'upstream label' used in Flood modeller.
   - **unit_name_ds(str)**: 'downstream_label' in Flood Modeller or None if the
     unit does not have a downstream label.
   - **unit_type(str)**: the same amoung all units of the same type (e.g. 'usbpr')
   - **unit_category(str)**: the same amoung all units of the same category (e.g. 'bridge')

In addition to these variables there are two other key components to all units:

   - **head_data(dict)**: single variables associated with the unit. The dict
     stores HeadDataItem objects.
   - **row_data(dict)**: variable length data associated with the unit. The 
     dict stores RowDataCollection objects.
   
head_data and row_data are the components that you will spend most of the time
working with.


#########
Head Data
#########

The head_data dict contains HeadDataItem objects. These contain rules for 
storing all of the single variables in a particular unit. An example of the
kind of data stored here for the RiverUnit would be: 'distance', 'lateral1',
'slope', etc.

Currently HeadDataItem's store four different types of data:

   - float
   - int
   - string
   - tuple
   
The only one that needs explaining is the tuple. This is a tuple of possible
values that can be set for that item. As an example in the BridgeUnit the
'pier_shape' HeadDataItem is set to only allow the values ('FLAT', 'ARCH'),
because they are the allowed values in the FMP bridge units. If you try to
add a variable that isn't supported by HeadDataItem it will raise a ValueError.

The individual AUnit types in the datunits package should all contain a 
summary of the values that their specific HeadDataItem's support.


Accessing and updating
======================

All the head_data values can be accessed like so::

   # get the value
   slope = river.head_data['slope'].value
   
   # change the value
   river.head_data['distance'].value = 32.5
   

########
Row Data
########

The row_data is also a dict, although for a lot of units it will only contain
one entry: 'main'. The primary dict in all of the units will be called 'main' 
rather than something specific to make it easier to remember. Some units will 
contain no row_data (row_data == {}) and some others may have multiple row_data 
entries, such as BridgeUnitUsbpr which also has 'culvert' and 'opening'. It
will depend on how many variable length dataset the unit has. It shoud be 
apparent from knowledge of the component in Flood Modeller how many dicts it 
will have. 

The values of the row_data dict are RowDataCollection objects. The 
RowDatacollection class is a collection of data pertaining to the loaded row
data. For further information see :ref:`rowdatacollection-top`.

**Important** 
*You should never add/remove items to/from the row_data dict. It is setup in*
*the class constructor and is relied on by a lot of the codebase. If you change*
*it you will probably get a lot of errors.*


Accessing and updating
======================

*For more fine grained control of accessing and updating the data within the*
*RowDataCollection's you should use the RowDataCollection itself*.

When accessing data in RowDataCollection's held by an AUnit type more
functionality is available in the methods within the RowDataCollection itself.
There is though a couple of convenience hooks in the AUnit interface for 
common requests. These include:
   
   - rowDataObj(key, rowdata_type='main'): to return one of the DataObject's in
     the RowDataCollection.
   - row(index, rowdata_type='main'): to return the contents of a particular
     row in a RowDataCollection.
     
example::

   # Assume we have RiverUnit called river.
   from ship.fmp.datunits import ROW_DATA_TYPES as rdt
   
   # Returns the ROUGHNESS DataObject from the row data in the 'main' row_data
   dobj = river.rowDataObj(rdt.ROUGNESS)
   
   # You can now get at the data in this (note you shouldn't ever add any new
   # data to a DataObject directly, you should use the addRow method in the
   # RowDataCollection that keeps track of the data sanity. Although you can
   # update values if wanted. For example:
   for i, item in enumerate(dobj):
      dobj[i] = item * 1.2

The AUnit types contain some methods for adding and removing rows from the
RowDataCollection's:
   
   - **addRow()**: add a new row to a specific row_data item.
   - **updateRow()**: alter the data in a specific row_data item.
   - **deleteRow()**: delete a row from a specific row_data item.
   
Add Row
-------

The addRow allows you to add a new row to one of the RowDataCollection objects
in the row_data dict. It must have a row_vals argument. This is a dict that
contains the values you want to add to the row. The values of this dict will
vary depending on the type of unit you are adding it to. The keys of the
row_vals dict use the ROW_DATA_TYPES enum in the datunits package .__init__.py
file. To use RiverUnit as an example::

   # import the ROW_DATA_TYPES
   from ship.fmp.datunits import ROW_DATA_TYPES as rdt

   # A complete row_vals dict for RiverUnit
   row_vals = {
                  rdt.CHAINAGE: 12.5, rdt.ELEVATION: 35.0, rdt.ROUGHNESS: 0.04,
                  rdt.PANEL_MARKER: True, rdt.RPL: 1.0, rdt.BANKMARKER: False,
                  rdt.EASTING: 0.00, rdt.NORTHING: 0.00, rdt.DEACTIVATION: False,
              }
   
   # Appends a new row to the end of the 'main' RowDataCollection
   dat.addRow(row_vals)
   
   # However most units will set defaults for the values that they can
   # So this will work as well
   row_vals = {
                  rdt.CHAINAGE: 12.5, rdt.ELEVATION: 35.0
              }
   dat.addRow(row_vals)

   # Check the docs for individual units to see which ones are set as default.

As well as the row_vals the addRow method takes two optional arguments:

   - **rowdata_type(str)**: the key to the row_data entry to update. Default == 'main'.
   - **index(int)**: the index to add the row at. If not supplied it will be 
     appended to the end of the RowDatacollection.

Update Row
----------

The updateRow allows you to update some or all of the values in a particular
entry in a RowDataCollection. It is the same as addRow except the index is not 
an optional argument.

Delete Row
----------

The deleteRow method deletes a row from a specific RowDataCollection. You
must provide an index and an options row_data key.


#######################
Unit specfic attributes
#######################

The docstrings within all of the AUnit classes in the datunits package contain
class specific information about the head_data variables and row_data entries.
