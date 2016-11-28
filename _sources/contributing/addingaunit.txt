.. _addaunit-top:

******************
Adding a new AUnit
******************

If you're thinking about adding a new FMP unit type the best approach is to 
have a look at the RiverUnit. It's reasonably simple, but includes everything 
that is supported in some way.

When adding a new unit the steps you need to take are:

   - Create a new module for the new unit.
   - Implement some required interfaces.
   - Add the class to the FmpUnitFactory.
   - Add a test module for the new unit.
   - Add an entry to the unitdescriptions.rst file in the docs.

########################
Create a new unit module
########################

Create a new module under the fmp.datunits package and call it the name of the
unit that you are creating. Generally units that share behaviour are all stored
in the same module, but define separate classes. BridgeUnitArch and 
BridgeUnitUsbpr are good examples. The bridgunit.py module contains three
classes:

   - **BridgeUnit**: asbstract class.
   - **BridgeUnitArch**: concrete implementation of the Arch Bridge.
   - **BridgeUnitUsbpr**: concrete implementation of the Usbpr Bridge.

BridgeUnitArch and BridgeUnitUsbpr both inherit from BridgeUnit. BridgeUnit
defines functionality that is shared across all of the bridges.

#############################
Implement required interfaces
#############################

All AUnit types need to implement several interfaces. Some are for loading data
in from files and some are for amending an existing unit. The interfaces that
are required can vary slightly depending on the kind of data that a unit holds.

You must implement:

   - **readUnitData()**: to read in data from a file. This is called by the 
     FmpUnitFactory createUnitFromFile() method when loading a .dat/.ied file.
   - **getData()**: to return the formatted unit data. This is called by the
     DatCollections getPrintableData() method when returning a formatted file.

In addition to these methods you must override a couple of class constants:

   - **AUnit.UNIT_TYPE**: should be the name of the unit type (e.g. 'arch' for a
     BridgeUnitArch and 'usbpr' for BridgeUnitUsbpr. It must be a unique
     identifier.
   - **AUnit.UNIT_CATEGORY**: should be the category the unit sits in (e.g. 'bridge'
     for both of the above BridgeUnit's.
   - **AUnit.FILE_KEY**: this is the first whole word of the line in the .dat/.ied
     file that indicates the unit type (e.g. 'RIVER' for RiverUnit or the first
     work 'INITIAL' from 'INITIAL CONDITIONS' in the InitialConditionsUnit.
   - **AUnit.FILE_KEY2**: the first whole word of the following line in the .dat/
     .ied file that indicates the sub type (e.g. 'SECTION' for RiverUnit or
     'USBPR1978' for BridgeUnitUsbpr. Not all units have this. If it doesn't
     then set it to None.

As well as these there is an optional method you should override if the unit
needs to be included in the initial conditions:

   - **icLabels()**: this should return a list with all of the labels that must be
     included in the initial conditions. RiverUnit, for example, returns a list
     with a single entry [self.name]. Both bridge units return a list with two
     entries [self.name, self.name_ds]. If the type of unit has no initial 
     conditions it doesn't need to override this method.
     
####################
Constructor behavior
####################

In the constructor you should make sure that you instantiate the following
member variables:

   - Set two member variables self.unit_type and self.unit_category equal to 
     UNIT_TYPE and UNIT_CATEGORY respectively in the constructor.
   - Set self.head_data equal to a dict of HeadDataItems (see below).
   - Set self.row_data equal to a dict of RowDataCollections, IF the unit has
     variable length row data. If it doesn't you don't need to override this
     variable.
     
Setting up the head_data dict should be done like so::

   # Using part of BridgeUnitArch head_data as an example
   # The key for each entry should be similar to the name in the FMP GUI and/or
   # the .dat file overview in Help, whichever is clearer. Usually prefer the 
   # GUI. 
   # See HeadDataItem in fmp.head_data.py for more info, but, as a quick summary
   # it takes:
   #  - an intial value
   #  - a format str.
   #  - a row number (zero indexed)
   #  - a column number (zero indexed)
   #  - a data_type (see ship.datastructures.DATA_TYPES).
   #  - **kwargs (see HeadDataItem)
   self.head_data = {
         'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
         'remote_ds': HeadDataItem('', '{:<12}', 2, 3, dtype=dt.STRING),
         'roughness_type': HeadDataItem('MANNING', '{:<8}', 3, 0, dtype=dt.CONSTANT, choices=('MANNING',)),
         'calibration_coef': HeadDataItem(1.000, '{:>10}', 4, 0, dtype=dt.FLOAT, dps=3),
         'num_of_orifices': HeadDataItem(0, '{:>10}', 4, 4, dtype=dt.INT),
     }

The values that are handed in to head_data will be checked against the type so
make sure you choose the correct one. If something can be either a string value
or a float, choose STRING. If only certain values (like keywords) are allowed
then choose CONSTANT, which takes a tuple of allowed values. If it can take
empty values or you can use default values send them as kwargs (see HeadDataItem).

Then you need to setup any required RowDataCollections. Using BridgeUnitArch
as an example. It requires two entries in row_data, for geometry and bridge
openings (these are actually instantiated in BridgeUnit)::

   # There are two ways to instantiate a RowDataCollection, but this way is
   # neater. Note that the RowDataCollection - usually geometry - should 
   # always be called 'main'.
   # Here we create a list of DataObject's (ship.datastructures.dataobject.py)
   # They take a:
   #  - ROW_DATA_TYPE (see ship.fmp.datunits.__init__.py) Try to use an existing
   #    one if applicable.
   #  - format string.
   #  - **kwargs: useful ones are default (value to use if none is given when
   #    creating a new row) and no_of_dps (decimal places). 
   main_dobjs = [
         do.FloatData(rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3, update_callback=self.checkIncreases),
         do.FloatData(rdt.ELEVATION, format_str='{:>10}', no_of_dps=3),
         do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', no_of_dps=3, default=0.039),
         do.ConstantData(rdt.EMBANKMENT, ('', 'L', 'R'), format_str='{:>11}', default=''),
     ]
     
     # With this approach you use the bulkInitCollection method. Note that the
     # order of the DataObject's will be defined by the order of the list. This
     # has implications in the order that's read out when calling getData() and
     # a couple of other places. Basically alway set the order in line with the
     # column order in the .dat file.
     self.row_data['main'] = RowDataCollection.bulkInitCollection(main_dobjs) 
     
     # Finally call the setDummyRow method and set send any non default (or values
     # you don't want the default to be used for) values. This is created to 
     # begin with so that users that create units but add no row data before 
     # saving won't get errors when opening in Flood Modeller.
     self.row_data['main'].setDummyRow({rdt.CHAINAGE: 0, rdt.ELEVATION: 0,
                                        rdt.ROUGHNESS: 0})
     
     # Same process again, this time for the opening data.
     open_dobjs = [
         do.FloatData(rdt.OPEN_START, format_str='{:>10}', no_of_dps=3, update_callback=self.checkOpening),
         do.FloatData(rdt.OPEN_END, format_str='{:>10}', no_of_dps=3, update_callback=self.checkOpening),
         do.FloatData(rdt.SPRINGING_LEVEL, format_str='{:>10}', no_of_dps=3, default=0.0),
         do.FloatData(rdt.SOFFIT_LEVEL, format_str='{:>10}', no_of_dps=3, default=0.0),
     ]
     self.row_data['opening'] = RowDataCollection.bulkInitCollection(open_dobjs) 
     self.row_data['opening'].setDummyRow({rdt.OPEN_START: 0, rdt.OPEN_END: 0})

############
readUnitData
############

The readUnitData method is called by the FmpUnitFactory when loading a file. 
The AUnit type is completely responsible for how it's section of the file is
loaded. This is obviously not ideal, but the alternative (as far as I can see)
is to do a lot of additional file parsing and adding a lot more variables and
back and forth (if you have a better idea for this please let me know!). The
readUnitData method is handed the following variables:

   - **unit_data(list)**: containing all of the lines in the loaded file. This sounds
     awfull, and it kind of is, but it's only a reference so doesn't actually
     add lots of additional overhead. It does give the unit complete power over
     the load process though, so you need to get this right.
   - **file_line(int)**: the current line being read in the unit_data list.

When reading the file contents in you must do the following. Note that this
example uses RiverUnit. The RiverUnit splits the data reading process into two
separate methods: _readHeadData and _readRowData to make things a bit easier
to read. For reference the actual readUnitData method looks like this::

   file_line, unit_length = self._readHeadData(unit_data, file_line)
   file_line = self._readRowData(unit_data, file_line, (file_line + unit_length))
   
   # Note here that you need to return the fileline index that contains the
   # the last line of the data you have been reading. This is because it will
   # be incremented in the DatLoader loading loop when returned. 
   return file_line - 1

Update the head_data (_readHeadData() in RiverUnit)::

   # Populate the head_data by splitting the strings. Be careful with this as
   # .dat files are very particular about the formatting of the lines.
   self.head_data['comment'].value = unit_data[file_line + 0][5:].strip()
   self._name = unit_data[file_line + 2][:12].strip()
   self.head_data['spill1'].value = unit_data[file_line + 2][12:24].strip()
   self.head_data['spill2'].value = unit_data[file_line + 2][24:36].strip()
   self.head_data['lateral1'].value = unit_data[file_line + 2][36:48].strip()
   self.head_data['lateral2'].value = unit_data[file_line + 2][48:60].strip()
   self.head_data['lateral3'].value = unit_data[file_line + 2][60:72].strip()
   self.head_data['lateral4'].value = unit_data[file_line + 2][72:84].strip()
   self.head_data['distance'].value = unit_data[file_line + 3][0:10].strip()
   self.head_data['slope'].value = unit_data[file_line + 3][10:30].strip()
   self.head_data['density'].value = unit_data[file_line + 3][30:40].strip()

   # Here it returns the file line number set to the next line
   return file_line + 4

Update all row_data. This may be the first of multiple row_data entries, like
in BridgeUnitUsbpr which has 'main', 'opening' and 'culvert'::

   # Get the number of rows 
   end_line = int(unit_data[file_line].strip())
   file_line += 1
   try:
      # Load the geometry data
      for i in range(file_line, end_line):
          chain   = unit_data[i][0:10].strip()
          elev    = unit_data[i][10:20].strip()
          rough   = unit_data[i][20:30].strip()
          panel   = unit_data[i][30:35].strip()
          rpl     = unit_data[i][35:40].strip()
          bank    = unit_data[i][40:50].strip()
          east    = unit_data[i][50:60].strip()
          north   = unit_data[i][60:70].strip()
          deact   = unit_data[i][70:80].strip()
          special = unit_data[i][80:90].strip()
          
          # Sometimes certain values can be missing in the .dat files so we
          # check for those here
          if east == '': east = None
          if north == '': north = None
          
          # Add the parsed row data value as a new row in the RowDataCollection
          self.row_data['main'].addRow(
              {rdt.CHAINAGE: chain, rdt.ELEVATION: elev, rdt.ROUGHNESS: rough,
               rdt.RPL: rpl, rdt.PANEL_MARKER: panel, rdt.BANKMARKER: bank, 
               rdt.EASTING: east, rdt.NORTHING: north, 
               rdt.DEACTIVATION: deact, rdt.SPECIAL: special
          }) 
          
   except NotImplementedError:
      logger.ERROR('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
      raise
         
     return end_line

Then, as noted above, you need to return the file_line int value with it set to
the index of the last line that contains this units data.

#######
getData
#######

The getData method is just the reverse of the readUnitData. You take the data
stored in the AUnit and you return it ready for saving to a .dat file. For 
head_data this involves (BridgeUnitArch again)::

   out = []
   
   # Put the FILE_KEY at the top and the comment next to it with one space
   out.append('BRIDGE ' + self.head_data['comment'].value)
   
   # Then FILE_KEY2 if it has one
   out.append('ARCH')
   
   # From now on it's unit specific. Here it's all of the unit labels.
   out.append('{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds) +
                  self.head_data['remote_us'].format() + self.head_data['remote_ds'].format())
                  
   # Then the roughness type
   out.append(self.head_data['roughness_type'].value)
   
   # Then everything else. This is where the format_str in HeadDataItem comes
   # in. Note that it's called in the key_order loop
   key_order = [
      'calibration_coef', 'skew_angle', 'width', 'dual_distance', 'num_of_orifices',
      'orifice_flag', 'op_lower', 'op_upper', 'op_cd'
   ]
   temp = []
   for k in key_order:
      temp.append(self.head_data[k].format())
   
   # Do whatver you want to get this formatted. I like to get everything added
   # to a list and then just join it and split on newlines.
   out += ''.join(temp).split('\n')

   return out

Getting row_data is similar, but actually even easier because it's pretty much
all taken care of by the RowDataCollection and DataObject's that we setup to
copy with this earlier (Using the 'main' bridge row_data)::

   out_data = []
   
   # Get the number of rows and add it to the list
   no_of_rows = self.row_data['main'].numberOfRows()
   out_data.append('{:>10}'.format(no_of_rows))
   
   # Loop through all of the rows and call the getPrintableRow(index) method.
   # This calls the formatting methods in RowDataCollection and the DataObject's
   # which do all of the hard work for you.
   for i in range(0, no_of_rows): 
      out_data.append(self.row_data['main'].getPrintableRow(i))

   return out_data

And we're done. That's most of the hard work over.

###########################
Additional method overrides
###########################

Sometime you may want to override the addRow and setRow methods in AUnit. You
don't need to, but it can be useful it you want to do any additional checking
on the input row_vals data before handing it to the RowCollection. It also
let you give more informative error strings. See bridgeunit.py for some 
examples.

**Note**
*The RowDataCollection will check that it has all the values it needs to add*
*a new row already. It does this based on which of the DataObject's have a*
*default value. If it has one and no value has been provided it will use the*
*default. If it doesn't then it will raise an error.*

In RiverUnit (and lots of others) there is a kwarg handed to the DataObject::

   do.FloatData(rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3, 
                update_callback=self.checkIncreases)

You can hand any callback function to a DataObject (and a RowDataCollection)
and they will call them just before they add or update an item (or row). This
means you can catch issues when users bypass the AUnit methods and go straight
to the other objects. The update_callback function calls with the arguments:

   - **value**: the value being given to update with.
   - **index(int)**: the index of the value to be updated/added.

The particular one shown above (checkIncreases) is so commonly needed that it's
actually implemented in the AUnit class. It makes sure that the values in that
DataObject are alway >= to the value before them.


There may sometime be some specific behaviour that you will need to implement
for your unit type, but that covers most of the stuff you'll need.

##############################
Adding the unit to the factory
##############################

In order to get your unit to load you will need to add it to the imports and 
then add the class to the available_units list in the FmpUnitFactory::

   class FmpUnitFactory(object):
      
      # Add your unit to this class constant
      available_units = (
           isisunit.HeaderUnit,
           isisunit.CommentUnit,
           riverunit.RiverUnit, 
           refhunit.RefhUnit,
           icu.InitialConditionsUnit,
           ...,
      }

It will now load rather than be set as an UnknownUnit, like all the other parts
of the .dat/.ied file that it doesn't know what to do with :)

##################
Writing some tests
##################

Due to the amount of control over the loading process that individual units
have it's really important to make sure that the readUnitData and getData
methods are fully tested. These two methods MUST have test written for them.
If you put in any update_callback functions or overide the addRow/updateRow/
deleteRow methods you are strongly encouraged to put in tests for them as well.
*Note you don't need to test the checkIncreases callback as it's done already.*

Look at test_riverunit or any of the others in the tests folder for an example
of one way to test this functionality.

#########################
Add a summary to the docs
#########################

Once you've finished adding your unit you need to put a short summary of how
to use it to :ref:`unitdescriptions-top`. This is in the unitdescriptions.rst 
file in the docs/source/fmp folder. 
Have a look at some of the others for an example and copy the layout from them.
The docs are written in restructured text format and compiled with Sphinx. You
can go here for more info on Sphinx_:

.. _Sphinx: http://www.sphinx-doc.org/en/stable/rest.html

Or have a look at this cheatsheet_:

.. _cheatsheet: http://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html

####################
Issue a pull request
####################

And then you're done. If you could issue a pull request to let me know that
you've put a unit together that would be great. I'll check the code, run the
tests, check the integration tests and pull it in to the main repo. 

If you've got any questions on any of this or any other section that you would
like to contribute to please let me know.

Thanks.









