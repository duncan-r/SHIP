.. _updatechanges-top:

***********
API Changes
***********

There have a been a lot of changes to method names and a few classes when
finalising the updates from version 0.2.5 to 0.3.0. This are fixed now and
and further changes will be subject to deprecation.

**A major change to all TuflowFile and PathHolder classes is that the member**
***file_name* is now called *filename***. This has been bugging me for a long
time and it was also inconsistent throughout the API.

Most of the functions and methods in the filetools.py module have had the 'get'
removed from the front of the method name (e.g. getAbsolutePath is now just
'absolutePath'.

The changes to the tuflow package are too extensive to sum up in a short
changes summary. To see how it now works you should look at the docs. The ethos
for accessing data is still quite similar, it is just set out in a slightly
different way. 

Below is a list of the main changes to the isis (now fmp) package to ease the
transition of existing code. They are ordered by module.

**The biggest change for the isis package is the package name change from*
***isis* to *fmp*. Although it's probably the easiest to deal with.**


AIsisUnit/AUnit
###############

The abstract base class for all units in the fmp/isis package

   - Name changed from AIsisUnit to AUnit. The software name has changed and it
     seemed like now was a good time to get this update done.
   - Unit name is now exclusively stored in the AUnit.name member. Before it
     was in name and in head_data['section_label']. This was hard to keep in
     sync.
   - Downstream label is now exclusively stored in the AUnit._name_ds member.
     Before it was stored in head_data['lable_downstream'].
   - AUnit.has_data_rows member is no longer available. This value is not stored
     anymore, only calculated. There is a prooperty available called has_row_data.
   - row_collections and additional_row_collections no longer exist. All row
     data is now stored in a dict called row_data. All AUnit's that contain
     row data will definitely have the key 'main', which is usually geometry
     data. If there are other RowDataCollections they will be stored in this
     dict under a different name (e.g. 'opening' for BridgeUnitArch).

In order to make the API a little bit more pythonic and make the method/function
names a bit clearer (in some cases they had even shifted from oler functionality
and the names had not been updated!) some names have changed or been shifted to
property's. Pretty much any function/method with 'get' at the start has had the
'get' removed. This was a legacy from the initial Java implementation and is
not used in Python. These include:

   - getUnitVars: these are not longer used, so this is gone.
   - getName, getUnitType, getUnitCategory. These are either variables or 
     properties. To call them just use the variable name (e.g. .name,
     .unit_type, .unit_category).
   - getDeepCopy: now called copy.
   - getRowDataType: now called rowDataType.
   - getRow: now called row.
   - getHeadData: no longer used. Use the dict variable .head_data instead.
   - deleteDataRow: now called deleteRow.
   - updateDataRow: now called updateRow.
   - _checkChainageIncreaseNotNegative: now called check increases. This is
     mostly only used internally anyway. Note that the args list for this is
     different. It takes any series rather than just chainage.
     
The AUnit.head_data is now no longer a simple dict with values assigned. It is
a dict with ship.fmp.headdata.HeadDataItem's. This allows value to checked when
added and better constraints and error messages. It means that instead of 
accessing values as a normal dict you will need to do this::

   # assume we have a RiverUnit called river
   # old way - this no longer works
   distance = river.head_data['distance']
        
   # new way
   distance = river.head_data['distance'].value 
   
   # same with setting
   river.head_data['distance'].value = 12.5
   

DatCollection
#############

Not as much changed in here:

   - getIndex: changed to index.
   - getUnitsByCategory: changed to unitsByCategory.
   - getUnitsByType: changed unitsByType.
   - getUnit: changed to unit. Note that this also accepts an optional 
     unit_category arg now, as well as the optional unit_type arg.   
   - getNumberOfUnits: changed to numberOfUnits.
   
   
RowDataCollection
#################
   
Note that a bulkInitCollection classmethod has been added which takes a list of
DataObject's, rather than having to add each one separately.

Most of the changes in here are actually additions of new methods to make
accessing different types of data a little easier (see the docs for more info
on that). There are a few existing changes though.
Changes:

   - rowDataAsList: changed to toList.
   - addValue and setValue: changed to _addValue and _setValue. You probably
     shouldn't be calling these anyway (use addRow and setRow instead).
   - addNewRow: changed to addRow.
     

     
     
     
     
     