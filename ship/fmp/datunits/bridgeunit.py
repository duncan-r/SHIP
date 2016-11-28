"""

 Summary:
    Contains the BridgeUnit, BridgeUspbrUnit and BridgeArchUnit classed.
    The BridgeUnit is a superclass to the other containing default shared
    behaviour and content.
    These hold all of the data read in from the bridge units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

import math
from collections import OrderedDict

from ship.fmp.datunits.isisunit import AUnit
from ship.datastructures import dataobject as do
from ship.datastructures.rowdatacollection import RowDataCollection
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.headdata import HeadDataItem
from ship.utils.tools import geometry
from ship.datastructures import DATA_TYPES as dt



class BridgeUnit (AUnit): 
    """Subclass of AUnit storing Isis Bridge Unit data.

    Note:
        This really an abstract class for any bridge unit and is not really
        intended to be used directly.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, roughness, etc values.
    Methods for accessing the data in these objects and adding removing rows
    are available.
    """
    
    UNIT_TYPE = 'bridge'
    UNIT_CATEGORY = 'bridge'
    FILE_KEY = None
    FILE_KEY2 = None
    

    def __init__(self, **kwargs): 
        """Constructor.
        """
        AUnit.__init__(self, **kwargs)

        self._unit_type = BridgeUnit.UNIT_TYPE
        self._unit_category = BridgeUnit.UNIT_CATEGORY
        self._name = 'BrgUS'
        self._name_ds = 'BrgDS'

        self.setupRowData()
        
        

    def setupRowData(self):
        """Setup the main geometry and opening RowCollection's. 
        
        These are used by all BridgeUnits, but they're added to a method called
        by the constructor in cases anyone need to override them.
        """
        main_dobjs = [
            do.FloatData(rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3, update_callback=self.checkIncreases),
            do.FloatData(rdt.ELEVATION, format_str='{:>10}', no_of_dps=3),
            do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', no_of_dps=3, default=0.039),
            do.ConstantData(rdt.EMBANKMENT, ('', 'L', 'R'), format_str='{:>11}', default=''),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(main_dobjs) 
        
        open_dobjs = [
            do.FloatData(rdt.OPEN_START, format_str='{:>10}', no_of_dps=3, update_callback=self.checkOpening),
            do.FloatData(rdt.OPEN_END, format_str='{:>10}', no_of_dps=3, update_callback=self.checkOpening),
            do.FloatData(rdt.SPRINGING_LEVEL, format_str='{:>10}', no_of_dps=3, default=0.0),
            do.FloatData(rdt.SOFFIT_LEVEL, format_str='{:>10}', no_of_dps=3, default=0.0),
        ]
        self.row_data['opening'] = RowDataCollection.bulkInitCollection(open_dobjs) 
        
    
    def icLabels(self):
        return [self._name, self._name_ds]

        
    def numberOfOpenings(self):
        """
        """
        return self.row_data['opening'].numberOfRows()
    
    
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
         
        See Also:
            AUnit
             
        Args: 
            unit_data (list): The section of the isis dat file pertaining to 
                this section. 
        """
        file_line = self._readHeadData(unit_data, file_line)
        file_line = self._readMainRowData(unit_data, file_line)
        file_line = self._readAdditionalRowData(unit_data, file_line)
        file_line -= 1
        return file_line
        

    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        Note:
            Must be implemented by subclass
            
        Raises:
            NotImplementedError: if not overriden by sub class.
        """
        raise NotImplementedError


    def _readMainRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Bridge Units of the dat file.
        
        Args:
            unit_data (list): the data pertaining to this unit.
        """ 
        no_of_chainage_rows = int(unit_data[file_line].strip())
        file_line += 1
        out_line = file_line + no_of_chainage_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):

                chain   = unit_data[i][0:10].strip()
                elev    = unit_data[i][10:20].strip()
                rough   = unit_data[i][20:30].strip()
                try:
                    bank = unit_data[i][40:51].strip()
                except:
                    bank = None
                
                self.row_data['main'].addRow({
                    rdt.CHAINAGE: chain, rdt.ELEVATION: elev, 
                    rdt.ROUGHNESS: rough, rdt.EMBANKMENT: bank
                })
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise

        return out_line
    

    def getData(self): 
        """Retrieve the data in this unit.

        See Also:
            AUnit - getData()
            
        Returns:
            String list - output data formated the same as in the .DAT file.
        """
        out_data = self._getHeadData()
        out_data.extend(self._getRowData()) 
        out_data.extend(self._getAdditionalRowData())
        return out_data
    
    
    def _formatDataItem(self, item, col_width, no_of_dps=None,
                                    is_head_item=True, align_right=True):
        """Format the given head data item for printing to file.
        """
        if is_head_item:
            item = self.head_data[item]
        if not no_of_dps == None:
            if not item == '':
                form = '%0.' + str(no_of_dps) + 'f'
                item = form % float(item)
        
        if align_right:
            final_str = '{:>' + str(col_width) + '}'
        else:
            final_str = '{:<' + str(col_width) + '}'
        return final_str.format(item)
  
  
    def _getRowData(self):
        """For all the rows in the river geometry section get the data from
        the rowdatacollection class.

        Returns:
            list - containing the formatted unit rows.
        """
        out_data = []
        no_of_rows = self.row_data['main'].numberOfRows()
        out_data.append(self._formatDataItem(no_of_rows, 10, is_head_item=False))
        for i in range(0, no_of_rows): 
            out_data.append(self.row_data['main'].getPrintableRow(i))
        
        return out_data
    
    
    def _getAdditionalRowData(self):
        """Get the formatted row data for any additional row data objects.
         
        Returns:
            list - containing additional row data.
        """
        raise NotImplementedError
   
  
    def _getHeadData(self):
        """Get the header data formatted for printing out
        
        Note:
            Must be implemented by concrete subclass.
        
        Raises:
            NotImplementedError: if not overridden by sub class
        """
        raise NotImplementedError
    
   
    def updateRow(self, row_vals, index, collection_name=None):
        """Updates the row at the given index in the river units row_collection.
        
        The row will be updated at the given index. 

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index: the row to update. 
            collection_name=None(str): If None the self.row_collection
                with the bridges geometry data will be updated. If a string it
                will be looked for in the self.additional_row_collections
                dictionary or raise an AttributeError if it doesn't exist.

        Raises:
            KeyError: If collection_name key does not exist.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not collection_name is None:
            if not collection_name in self.additional_row_collections.keys():
                raise KeyError ('collection_name %s does not exist in row collection' % (collection_name))
        
        # Call superclass method to add the new row
        AUnit.updateRow(self, index=index, row_vals=row_vals)
    
   
    def addRow(self, row_vals, rowdata_key='main', index=None): 
        """Adds a new row to one of this bridge units row_collection's.
        
        The new row will be added at the given index. If no index is given it
        will be appended to the end of the collection.
        
        If no chainage or elevation values are given an AttributeError will be 
        raised as they cannot have default values. All other values can be
        ommitted. If they are they will be given defaults.
        
        Examples:
            >>> import ship.fmp.datunits.rdt as rdt
            >>> unit.addRow({rdt.CHAINAGE:5.0, rdt.ELEVATION:36.2}, index=4)

        Args:
            row_vals(Dict): keys must be datunits.rdt with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index=None(int): the row to insert into. The existing row at the
                given index will be moved up by one.
            collection_name=None(str): If None the self.row_collection
                with the bridges geometry data will be updated. If a string it
                will be looked for in the self.additional_row_collections
                dictionary or raise an AttributeError if it doesn't exist.

        Raises:
            AttributeError: If required values are not given for the rowdata_key
                collection. See _checkRowKeys().
            KeyError: if the collection_name does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        self._checkRowKeys(row_vals, rowdata_key)
        AUnit.addRow(self, row_vals=row_vals, rowdata_key=rowdata_key, index=index)
    
    
    def _checkRowKeys(self, row_vals, rowdata_key):
        """Ensure certain values exist and are sane when updating a row.
        
        if rowdata_key == opening checks on the values will be made.
        SOFFIT_LEVEL must be >= SPRINGING_LEVEL.
        OPEN_END must be > OPEN_START.
        
        if rowdata_type == 'main' rdt.CHAINAGE and rdt.ELEVATION must be 
        given. if rowdata_type == 'opening' rdt.OPEN_START and rdt.OPEN_END
        must be given.
        
        Args:
            row_vals(dict): {ROW_DATA_TYPE: value} to update with.
            rowdata_key(str): the self.row_data dict key to update.
        
        Raises:
            AttributeError: if the required row_vals are not provided.
        """
        keys = row_vals.keys()
        if rowdata_key == 'main':
            if not rdt.CHAINAGE in keys or not rdt.ELEVATION in keys:
                logger.error('Bridge: Required values of CHAINAGE and ELEVATION not given')
                raise AttributeError('Bridge: row_vals must include CHAINAGE and ELEVATION.')

        elif rowdata_key == 'opening':
            if not rdt.OPEN_START in keys or not rdt.OPEN_END in keys:
                logger.error('Bridge: Required values of OPEN_START and OPEN_END not given')
                raise AttributeError('Bridge: row_vals must include OPEN_START and OPEN_END.')
            if not row_vals[rdt.OPEN_END] > row_vals[rdt.OPEN_START]:
                logger.error('Bridge: OPEN_END must be > than OPEN_START')
                raise AttributeError('Bridge: OPEN_END must be > than OPEN_START')
            if rdt.SOFFIT_LEVEL in keys and rdt.SPRINGING_LEVEL in keys:
                if not row_vals[rdt.SOFFIT_LEVEL] >= row_vals[rdt.SPRINGING_LEVEL]:
                    logger.error('Bridge: SOFFIT_LEVEL must be >= SPRINGING_LEVEL')
                    raise AttributeError('Bridge: SOFFIT_LEVEL must be >= SPRINGING_LEVEL')
                
 
    
    def checkOpening(self, data_obj, value, index):
        """Ensures that the bridge opening values are ok.
        
        OPEN_END must be > OPEN_START on the same row.
        OPEN_START must be > than OPEN_END on a previous row.
        OPEN_END must be > OPEN_START on a previous row.
        
        Args:
            data_obj(RowDataObj): to check the values for.
            value(float): the new value to check.
            index(int): the index the value will be inserted or updated at.
        
        Raises:
            ValueError - if value failes tests at index.
        """
        details = self._getAdjacentDataObjDetails(data_obj, value, index)

        if data_obj.data_type == rdt.OPEN_START:
            if details['prev_value']:
                if not value > details['prev_value']:
                    raise ValueError('Bridge: OPEN_START must be > than previous value')
                if not value > self.row_data['opening'].dataObject(rdt.OPEN_END)[details['prev_index']]:#.getValue(details['prev_index']):
                    raise ValueError('Bridge: OPEN_START must be > than previous OPEN_END value')
            if details['next_value']:
                if not value < details['next_value']:
                    raise ValueError('Bridge: OPEN_START must be < than next OPEN_START value')

        elif data_obj.data_type == rdt.OPEN_END:
            if details['prev_value']:
                if not value > details['prev_value']:
                    raise ValueError('Bridge: OPEN_END must be > than previous OPEN_END value')
                if not value > self.row_data['opening'].dataObject(rdt.OPEN_START)[details['index']]:#.getValue(details['index']):
                    raise ValueError('Bridge: OPEN_END must be > than OPEN_START value')
            if details['next_value']:
                if not value < details['next_value']:
                    raise ValueError('OBridge: PEN_END must be < than next OPEN_END value')
                if not value > self.row_data['opening'].dataObject(rdt.OPEN_START)[details['next_index']]:#.getValue(details['next_index']):
                    raise ValueError('Bridge: OPEN_END must be < than next OPEN_START value')
            
        
    def area(self):
        """Returns the cross sectional area of the bridge openings.    
        
        Return:
            Dict - containing the area of the opening(s). keys = 'total', then
                '1', '2', 'n' for all openings found.
        """
        return 0
#         areas = []
#         opening_data = self.additional_row_collections['Opening']
#         x_vals = self.row_collection.getRowDataAsList(rdt.CHAINAGE)
#         y_vals = self.row_collection.getRowDataAsList(rdt.ELEVATION)
#         
#         start_vals = opening_data.getRowDataAsList(rdt.OPEN_START)
#         end_vals = opening_data.getRowDataAsList(rdt.OPEN_END)
#         soffit_vals = opening_data.getRowDataAsList(rdt.SOFFIT_LEVEL)
#         springing_vals = opening_data.getRowDataAsList(rdt.SPRINGING_LEVEL)
#         openings = zip(start_vals, end_vals, soffit_vals, springing_vals)
#         
#         for i, x in enumerate(x_vals):
#             
#             if math.fabs(x - ) 
#         
#         
#         i=0


class BridgeUnitUsbpr (BridgeUnit): 
    """Concrete implementation of BridgeUnit for USBPR type bridges.
    
    Contains methods that override superclass with USBPR specific variables
    and file read/write behaviour.
    """
    
    UNIT_TYPE = 'usbpr'
    UNIT_CATEGORY = 'bridge'
    FILE_KEY = 'BRIDGE'
    FILE_KEY2 = 'USBPR1978'


    def __init__(self, **kwargs): 
        """Constructor.
        
        See Also:
            BridgeUnit
        """
        BridgeUnit.__init__(self, **kwargs)
        
        self._unit_type = BridgeUnitUsbpr.UNIT_TYPE
        self._unit_category = BridgeUnit.UNIT_CATEGORY

        # Fill in the header values these contain the data at the top of the
        # section
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'remote_us': HeadDataItem('', '{:<12}', 2, 2, dtype=dt.STRING),
            'remote_ds': HeadDataItem('', '{:<12}', 2, 3, dtype=dt.STRING),
            'roughness_type': HeadDataItem('MANNING', '{:<7}', 3, 0, dtype=dt.CONSTANT, choices=('MANNING',)),
            'calibration_coef': HeadDataItem(1.000, '{:>10}', 4, 0, dtype=dt.FLOAT, dps=3),
            'skew_angle': HeadDataItem(0.000, '{:>10}', 4, 1, dtype=dt.FLOAT, dps=3),
            'width': HeadDataItem(0.000, '{:>10}', 4, 2, dtype=dt.FLOAT, dps=3),
            'dual_distance': HeadDataItem(0.000, '{:>10}', 4, 3, dtype=dt.FLOAT, dps=3),
            'num_of_orifices': HeadDataItem(0, '{:>10}', 4, 4, dtype=dt.INT),
            'orifice_flag': HeadDataItem('', '{:>10}', 4, 5, dtype=dt.CONSTANT, choices=('', 'ORIFICE')),
            'op_lower': HeadDataItem(0.000, '{:>10}', 4, 6, dtype=dt.FLOAT, dps=3),
            'op_upper': HeadDataItem(0.000, '{:>10}', 4, 7, dtype=dt.FLOAT, dps=3),
            'op_cd': HeadDataItem(0.000, '{:>10}', 4, 8, dtype=dt.FLOAT, dps=3),
            'abutment_type': HeadDataItem('3', '{:>10}', 5, 0, dtype=dt.CONSTANT, choices=('1', '2', '3')),
            'num_of_piers': HeadDataItem(0, '{:>10}', 6, 0, dtype=dt.INT),
            'pier_shape': HeadDataItem('FLAT', '{:<10}', 6, 1, dtype=dt.CONSTANT, choices=('FLAT', 'ARCH')),
            'pier_shape_2': HeadDataItem('', '{:<10}', 6, 2, dtype=dt.CONSTANT, choices=('FLAT', 'ARCH'), allow_blank=True),
            'pier_calibration_coef': HeadDataItem('', '{:>10}', 6, 3, dtype=dt.FLOAT, dps=3, allow_blank=True),
            'abutment_align': HeadDataItem('ALIGNED', '{:>10}', 7, 0, dtype=dt.CONSTANT, choices=('ALIGNED', 'SKEW')),
        }

        # Add an culvert RowCollection to self.row_data dict
        dobjs = [
            do.FloatData(rdt.INVERT, format_str='{:>10}', no_of_dps=3),
            do.FloatData(rdt.SOFFIT, format_str='{:>10}', no_of_dps=3),
            do.FloatData(rdt.AREA, format_str='{:>10}', no_of_dps=3, default=0.0),
            do.FloatData(rdt.CD_PART, format_str='{:>10}', no_of_dps=3, default=1.0),
            do.FloatData(rdt.CD_FULL, format_str='{:>10}', no_of_dps=3, default=1.0),
            do.FloatData(rdt.DROWNING, format_str='{:>10}', no_of_dps=3, default=1.0),
        ]
        self.row_data['culvert'] = RowDataCollection.bulkInitCollection(dobjs) 

    
    
    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        See Also:
            BridgeUnit
        """
        self.head_data['comment'].value = unit_data[file_line][6:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:24].strip()
        self.head_data['remote_us'].value = unit_data[file_line + 2][24:36].strip()
        self.head_data['remote_ds'].value = unit_data[file_line + 2][36:48].strip()
        self.head_data['calibration_coef'].value = unit_data[file_line + 4][:10].strip()
        self.head_data['skew_angle'].value = unit_data[file_line + 4][10:20].strip()
        self.head_data['width'].value = unit_data[file_line + 4][20:30].strip()
        self.head_data['dual_distance'].value = unit_data[file_line + 4][30:40].strip()
        self.head_data['num_of_orifices'].value = unit_data[file_line + 4][40:50].strip()
        self.head_data['orifice_flag'].value = unit_data[file_line + 4][50:60].strip()
        self.head_data['op_lower'].value = unit_data[file_line + 4][60:70].strip()
        self.head_data['op_upper'].value = unit_data[file_line + 4][70:80].strip()
        self.head_data['op_cd'].value = unit_data[file_line + 4][80:90].strip()
        self.head_data['abutment_type'].value = unit_data[file_line + 5][0:10].strip()
        self.head_data['num_of_piers'].value = unit_data[file_line + 6][:10].strip()
        self.head_data['pier_shape'].value = unit_data[file_line + 6][10:20].strip()
        self.head_data['pier_shape_2'].value = unit_data[file_line + 6][20:30].strip()
        self.head_data['pier_calibration_coef'].value = unit_data[file_line + 6][30:40].strip()
        self.head_data['abutment_align'].value = unit_data[file_line + 7][:10].strip()
       
        return file_line + 8


    def _readAdditionalRowData(self, unit_data, file_line):
        """Get any additional data rows.
        
        See Also:
            BridgeUnit
        """
        file_line = self._readArchRowData(unit_data, file_line)
        file_line = self._readCulvertRowData(unit_data, file_line)
        return file_line 
    

    def _readArchRowData(self, unit_data, file_line):
        """Load the data defining the openings in the bridge.
        
        Args:
            unit_data (list): the data pertaining to this unit.
            
        TODO:
            Change the name of this function to _readOpeningRowData.
        """ 
        no_of_opening_rows = int(unit_data[file_line].strip())
        file_line += 1
        out_line = file_line + no_of_opening_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                ostart   = unit_data[i][0:10].strip()
                oend     = unit_data[i][10:20].strip()
                spring   = unit_data[i][20:30].strip()
                soffit   = unit_data[i][30:40].strip()
                
                self.row_data['opening'].addRow({
                    rdt.OPEN_START: ostart, rdt.OPEN_END: oend, 
                    rdt.SPRINGING_LEVEL: spring, rdt.SOFFIT_LEVEL: soffit
                })
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
        
        return out_line
        
    
    def _readCulvertRowData(self, unit_data, file_line):
        """Load the data defining the culvert openings in the bridge.
        
        Args:
            unit_data (list): the data pertaining to this unit.
        
        TODO:
            These errors are cryptic here as they're very specific to the
            RowDataCollections being accessed. Perhaps these should be made a
            little more relevant by raising a different error. Or they could
            be dealt with better here.
        """ 
        no_of_culvert_rows = int(unit_data[file_line].strip())
        file_line += 1
        out_line = file_line + no_of_culvert_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                invert      = unit_data[i][0:10].strip()
                soffit      = unit_data[i][10:20].strip()
                area        = unit_data[i][20:30].strip()
                cd_part     = unit_data[i][30:40].strip()
                cd_full     = unit_data[i][40:50].strip()
                drowning    = unit_data[i][50:60].strip()
                
                self.row_data['culvert'].addRow({
                    rdt.INVERT: invert, rdt.SOFFIT: soffit, rdt.AREA: area, 
                    rdt.CD_PART: cd_part, rdt.CD_FULL: cd_full, 
                    rdt.DROWNING: drowning
                })
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
        
        return out_line
    
        
    def _getHeadData(self):
        """Return the extracted header data.
        
        See Also:
            BridgeUnit
        """
        out = []
        out.append('BRIDGE ' + self.head_data['comment'].value)
        out.append('\nUSBPR1978')
        out.append('\n' + '{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds) +
                        self.head_data['remote_us'].format() + self.head_data['remote_ds'].format())
        key_order = [
            'roughness_type', 'calibration_coef', 'skew_angle', 'width', 'dual_distance', 'num_of_orifices',
            'orifice_flag', 'op_lower', 'op_upper', 'op_cd', 'abutment_type',
            'num_of_piers', 'pier_shape', 'pier_shape_2', 'pier_calibration_coef',
            'abutment_align',
        ]
        for k in key_order:
            out.append(self.head_data[k].format(True))
        final_out = ''.join(out).split('\n')
        
        return final_out
    
    
    def _getAdditionalRowData(self):
        """Get the formatted row data for any additional row data objects.
        
        Returns:
            list - containing additional row data.
        """
        out_data = []

        no_of_rows = self.row_data['opening'].numberOfRows()
        out_data.append(self._formatDataItem(no_of_rows, 10, is_head_item=False))
        for i in range(0, no_of_rows):
            out_data.append(self.row_data['opening'].getPrintableRow(i))
        
        no_of_rows = self.row_data['culvert'].numberOfRows()
        out_data.append(self._formatDataItem(no_of_rows, 10, is_head_item=False))
        for i in range(0, no_of_rows):
            out_data.append(self.row_data['culvert'].getPrintableRow(i))
        
        return out_data
    
    
    def _checkRowKeys(self, row_vals, rowdata_key):
        """Overriddes superclass method.
        
        Checks culvert keys as well.
        """
        BridgeUnit._checkRowKeys(self, row_vals, rowdata_key)

        keys = row_vals.keys()
        if rowdata_key == 'culvert':
            if not rdt.INVERT in keys or not rdt.SOFFIT in keys:
                logger.error('Required values of INVERT, SOFFIT and AREA not given')
                raise AttributeError('Required values of INVERT, SOFFIT and AREA not given')
            
            if not row_vals[rdt.SOFFIT] > row_vals[rdt.INVERT]:
                raise ValueError('Bridge culvert: SOFFIT must be > INVERT')
        
        
    def checkOrifice(self, data_obj, value, index):
        """
        """
        pass

        

class BridgeUnitArch (BridgeUnit): 
    """Concrete implementation of BridgeUnit for USBPR type bridges.
    
    Contains methods that override superclass with USBPR specific variables
    and file read/write behaviour.
    """
    
    # Additional values to add to the constants list
    UNIT_TYPE = 'arch'
    UNIT_CATEGORY = BridgeUnit.UNIT_CATEGORY
    FILE_KEY = 'BRIDGE'
    FILE_KEY2 = 'ARCH'


    def __init__(self, **kwargs): 
        """Constructor.
        
        See Also:
            BridgeUnit
        """
        BridgeUnit.__init__(self, **kwargs)

        self._unit_type = BridgeUnitArch.UNIT_TYPE
        self._unit_category = BridgeUnit.UNIT_CATEGORY

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'remote_us': HeadDataItem('', '{:<12}', 2, 2, dtype=dt.STRING),
            'remote_ds': HeadDataItem('', '{:<12}', 2, 3, dtype=dt.STRING),
            'roughness_type': HeadDataItem('MANNING', '{:<8}', 3, 0, dtype=dt.CONSTANT, choices=('MANNING',)),
            'calibration_coef': HeadDataItem(1.000, '{:>10}', 4, 0, dtype=dt.FLOAT, dps=3),
            'skew_angle': HeadDataItem(0.000, '{:>10}', 4, 1, dtype=dt.FLOAT, dps=3),
            'width': HeadDataItem(0.000, '{:>10}', 4, 2, dtype=dt.FLOAT, dps=3),
            'dual_distance': HeadDataItem(0.000, '{:>10}', 4, 3, dtype=dt.FLOAT, dps=3),
            'num_of_orifices': HeadDataItem(0, '{:>10}', 4, 4, dtype=dt.INT),
            'orifice_flag': HeadDataItem('', '{:>10}', 4, 5, dtype=dt.CONSTANT, choices=('', 'ORIFICE')),
            'op_lower': HeadDataItem(0.000, '{:>10}', 4, 6, dtype=dt.FLOAT, dps=3),
            'op_upper': HeadDataItem(0.000, '{:>10}', 4, 7, dtype=dt.FLOAT, dps=3),
            'op_cd': HeadDataItem(0.000, '{:>10}', 4, 8, dtype=dt.FLOAT, dps=3),
        }
        
    
    def _getHeadData(self):
        """Return the extracted header data.
        
        See Also:
            BridgeUnit
        """
        out = []
        out.append('BRIDGE ' + self.head_data['comment'].value)
        out.append('ARCH')
        out.append('{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds) +
                        self.head_data['remote_us'].format() + self.head_data['remote_ds'].format())
        out.append(self.head_data['roughness_type'].value)
        key_order = [
            'calibration_coef', 'skew_angle', 'width', 'dual_distance', 'num_of_orifices',
            'orifice_flag', 'op_lower', 'op_upper', 'op_cd'
        ]
        temp = []
        for k in key_order:
            temp.append(self.head_data[k].format())
        out += ''.join(temp).split('\n')
        
        return out
        
    
    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        See Also:
            BridgeUnit
        """
        self.head_data['comment'].value = unit_data[file_line][6:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:24].strip()
        self.head_data['remote_us'].value = unit_data[file_line + 2][24:36].strip()
        self.head_data['remote_ds'].value = unit_data[file_line + 2][36:48].strip()
        self.head_data['calibration_coef'].value = unit_data[file_line + 4][:10].strip()
        self.head_data['skew_angle'].value = unit_data[file_line + 4][10:20].strip()
        self.head_data['width'].value = unit_data[file_line + 4][20:30].strip()
        self.head_data['dual_distance'].value = unit_data[file_line + 4][30:40].strip()
        
        # This doesn't get set by default in fmp so turn a blank str into 0
        orif = unit_data[file_line + 4][40:50].strip()
        try:
            orif = int(orif)
        except (ValueError, AttributeError):
            orif = 0

        self.head_data['num_of_orifices'].value = orif
        self.head_data['orifice_flag'].value = unit_data[file_line + 4][50:60].strip()
        self.head_data['op_lower'].value = unit_data[file_line + 4][60:70].strip()
        self.head_data['op_upper'].value = unit_data[file_line + 4][70:80].strip()
        self.head_data['op_cd'].value = unit_data[file_line + 4][80:90].strip()
       
        return file_line + 5


    def _readAdditionalRowData(self, unit_data, file_line):
        """Load the data defining the openings in the bridge.
        
        Args:
            unit_data (list): the data pertaining to this unit.
            
        TODO:
            Change the name of this function to _readOpeningRowData.
        """ 
        no_of_opening_rows = int(unit_data[file_line].strip())
        file_line += 1
        out_line = file_line + no_of_opening_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):

                ostart   = unit_data[i][0:10].strip()
                oend     = unit_data[i][10:20].strip()
                spring   = unit_data[i][20:30].strip()
                soffit   = unit_data[i][30:40].strip()
                
                self.row_data['opening'].addRow({
                    rdt.OPEN_START: ostart, rdt.OPEN_END: oend, 
                    rdt.SPRINGING_LEVEL: spring, rdt.SOFFIT_LEVEL: soffit
                })
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
        
        return out_line
        

    def _getAdditionalRowData(self):
        """Get the formatted row data for any additional row data objects.
        
        Returns:
            list - containing additional row data.
        """
        out_data = []
        no_of_rows = self.row_data['opening'].numberOfRows()
        out_data.append(self._formatDataItem(no_of_rows, 10, is_head_item=False))
        for i in range(0, no_of_rows):
            out_data.append(self.row_data['opening'].getPrintableRow(i))
        
        return out_data
    
    