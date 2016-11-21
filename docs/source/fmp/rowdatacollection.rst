.. _rowdatacollection-top:

*****************
RowDataCollection
*****************

The RowDataCollection class is used to store variable length data. Primarily
this is used for the fmp package AUnit classes (although it is used in some 
sections of the tuflow package as well).


########
Overview
########

RowDataCollection is essentially a container for DataObject's. Primarily the
difference between these two is:
   - RowDataCollection is used to access and update data within rows.
   - DataObject is used to access, update and store data of the same type,
     i.e. columns.
     
For example if we have the following (slightly shortened) RiverUnit setup:

+--------------+--------------+--------------+--------------+
|   Chainage   |  Elevation   |   Roughness  | Panel Marker |
+==============+==============+==============+==============+
|    0.00      |     10.0     |     0.04     |     Yes      |
+--------------+--------------+--------------+--------------+      
|    3.00      |     5.0      |     0.04     |     No       |
+--------------+--------------+--------------+--------------+
|    5.00      |     5.0      |     0.04     |     No       |
+--------------+--------------+--------------+--------------+  
|    6.00      |     10.0     |     0.04     |     Yes      |
+--------------+--------------+--------------+--------------+ 

There will be four DataObject's in this case, one for each of the coumns. These
will have four entries in each, one for each row. The RowDataCollection will
store these four DataObject's and provide methods for accessing the data by
row rather than column.


###########
Data Access
###########

**IMPORTANT**
*You should never try and add a new item to one of the DataObject's manually. It*
*is fundamental that the DataObject stay the same length as each other. If you*
*added a new row the the Chainage column, in the table above, but not the others*
*it wouldn't make any sense and FMP wouldn't load it. RowDataCollection checks*
*for this, amoungst other things, and will raise an error at some point if the*
*lengths get out of sync.*
**Always use the RowDataCollection methods to add or remove rows.**

**Note**
You will want to import the following for working with RowDataCollections::
   
   # Used to sprecify the data_type in DataObjects
   from ship.fmp.datunits import ROW_DATA_TYPES as rdt

Reading
=======

There are some functions for accessing the DataObject data, but to be honest if
you're going to update any of the values in them it's easier to retrieve the
specific DataObject from the RowDataCollection and use it directly.

The main method for accessing data in a RowDataCollection is row(). It returns 
a dict containing all values in a row at the given index.

Most of the time you are more likely to want to group the data by a particular
DataObject type. This can be done in several ways:
   - **toDict**: return a dict with ROW_DATA_TYPES as key and list of the values
     in the associated DataObject as the item.
   - **dataObj**: returns the dataObj at the given ROW_DATA_TYPE.
   - **dataObjAsList**: returns the values in the dataObject at the given index
     as a list.

Example::

   # assume we have already obtained a RiverUnit from the DatCollection
   # Also assume the RowDataCollection holds the data in the exammple table
   # above
   
   # returns a dict 
   rdc = river.row_data['main'].toDict()
   
   eq = (rdc == {
            rdt.CHAINAGE:     [0.00, 3.00, 5.00, 6.00],
            rdt.ELEVATION:    [10.00, 5.00, 5.00, 10.00],
            rdt.ROUHNESS:     [0.04, 0.04, 0.04, 0.04],
            rdt.PANEL_MARKER: [True, False, False, True],
        })
   # prints True
   print (eq)

   chainage = river.row_data['main'].dataObjAsList(rdt.CHAINAGE)
   
   # prints True
   print (chainage == [0.00, 3.00, 5.00, 6.00])

   # Fetch the actual DataObject itself under the ROOUGHNESS key
   dataobj = river.row_data['main'].dataObj(rdt.ROUGHNESS)
   
   # Can now access the DataObject directly
   for d in dataobj:
      print (d) # prints the value at the current index
   
   
Updating
========

There are very few occassions where you would want to use these directly in
this class. All fmp package AUnit classes provide methods for adding and
updating row data. These will also do further checks and any errors will be
more specific. So use those. This is also the case for most other users of
RowDataCollection.

There are a number of methods for updating the contents of a RowDataCollection.
Most of the methods that update or add a single value are mainly available for
internal use. It's easy to end up with unsynced DataObjects and you should 
avoid it.

The two methods that should be used are:
   - **addRow**: add a new row to the collection.
   - **updateRow**: set the values at a given index.
   
Both of these methods take two arguments: a dict of row values and an index to
add the row / update an existing row.

   
