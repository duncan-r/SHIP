"""

 Summary:
    Contains the Refh class.
    This holds all of the data read in from the refh units in the dat file.
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

from ship.isis.datunits.isisunit import AIsisUnit
from ship.data_structures.rowdatacollection import RowDataCollection 


import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class RefhUnit(AIsisUnit): 
    """Concrete implementation of AIsisUnit storing Isis River Unit
    data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, roughness, etc values.

    Methods for accessing the data in these objects and adding removing rows
    are available.
    
    See Also:
        AIsisUnit
    """
    
    UNIT_TYPE = 'Refh'
    CATEGORY = 'Inflows'
    FILE_KEY = 'REFHBDY'


    def __init__(self): 
        """Constructor.
        """
        AIsisUnit.__init__(self)

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels.
        self.head_data = {'revision': 1, 'comment': '', 'section_label': '',
                          'z': '', 'easting': '', 'northing': '', 
                          'time_delay': 0.0, 'time_step': 0.0, 'bf_only': '',
                          'sc_flag': '', 'scale_factor': 0.0, 
                          'hydrograph_mode': '', 'hydrograph_scaling': '',
                          'min_flow': 0.0, 'catchment_area': 0.0,
                          'saar': 0, 'urbext': 0.0, 'season': '', 
                          'published_report': '', 'urban': '',
                          'subarea_1': 0.0, 'dplbar_1': 0.0, 'suburbext_1': 0.0,
                          'calibration_1': 0.0, 'subarea_2': 0.0, 'dplbar_2': 0.0, 
                          'suburbext_2': 0.0, 'calibration_2': 0.0, 
                          'subrunoff_2': 0.0, 'sewer_rp_2': '', 'sewer_depth_2': 0.0,
                          'sewer_loss_vol_2': '', 'subarea_3': 0.0, 'dplbar_3': 0.0, 
                          'suburbext_3': 0.0, 'calibration_3': 0.0, 
                          'subrunoff_3': 0.0, 'storm_area': 0.0, 
                          'storm_duration': 0.0, 'sn_rate': 0,
                          'rainfall_flag': '', 'arf_flag': '',
                          'rainfall_comment': '', 'rainfall_od': 0.0,
                          'return_period': 0, 'arf': 0.0, 'c': 0.0, 'd1': 0.0,
                          'd2': 0.0, 'd3': 0.0, 'e': 0.0, 'f': 0.0, 
                          'rp_flag': '', 'scf_flag': '', 'scf': 0.0, 'unknown': 0,
                          'storm_rows': 0, 'cmax_flag': '', 'cini_flag': '',
                          'alpha_flag': '', 'models_comment': '', 'cm_dcf': 0.0,
                          'cmax': 0.0, 'cini': 0.0, 'alpha': 0.0, 'bfihost': 0.0,
                          'uh_flag': '', 'tp_flag': '', 'up_flag': '',
                          'uk_flag': '', 'tp_dcf': 0.0, 'tp0': 0.0, 'tpt': 0.0,
                          'dplbar': 0.0, 'dpsbar': 0.0, 'propwet': 0.0,
                          'up': 0.0, 'uk': 0.0, 'uh_rows': 0, 'uh_units': 0,
                          'uh_fctr': 0.0, 'bl_flag': '', 'br_flag': '',
                          'br0_flag': '', 'bl_dcf': 0.0, 'bl': 0.0, 'br_dcf': 0.0,
                          'br': '', 'bf0': 0.0                          
                          } 

        self.unit_type = RefhUnit.UNIT_TYPE
        self.unit_category = RefhUnit.CATEGORY
        self.has_datarows = True
        self.unit_length = 0
        self.has_urban = False
        self.storm = []
    
        
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        See Also:
            AIsisUnit - readUnitData for more information.
        
        Args:
            unit_data (list): The section of the isis dat file pertaining 
                to this section 
        """
        file_line = self._readHeadData(unit_data, file_line)
        self._name = self.head_data['section_label']
        file_line = self._readStormData(unit_data, file_line)
        file_line = self._readSuffix(unit_data, file_line)
        return file_line
        

    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        Args:
            unit_data (list): containing the data to read.
        """
        self.head_data['revision'] = unit_data[file_line][18:19]
        self.head_data['comment'] = unit_data[file_line][20:].strip()
        self._name = self.head_data['section_label'] = unit_data[file_line + 1][:12].strip()
        self.head_data['z'] = unit_data[file_line + 2][:10].strip()
        self.head_data['easting'] = unit_data[file_line + 2][10:20].strip()
        self.head_data['northing'] = unit_data[file_line + 2][20:30].strip()
        self.head_data['time_delay'] = unit_data[file_line + 3][0:10].strip()
        self.head_data['time_step'] = unit_data[file_line + 3][10:20].strip()
        self.head_data['bf_only'] = unit_data[file_line + 3][20:30].strip()
        self.head_data['sc_flag'] = unit_data[file_line + 3][30:40].strip()
        self.head_data['scale_factor'] = unit_data[file_line + 3][40:50].strip()
        self.head_data['hydrograph_mode'] = unit_data[file_line + 3][50:60].strip()
        self.head_data['hydrograph_scaling'] = unit_data[file_line + 3][60:70].strip()
        self.head_data['min_flow'] = unit_data[file_line + 3][70:80].strip()
        self.head_data['catchment_area'] = unit_data[file_line + 4][0:10].strip()
        self.head_data['saar'] = unit_data[file_line + 4][10:20].strip()
        self.head_data['urbext'] = unit_data[file_line + 4][20:30].strip()
        self.head_data['season'] = unit_data[file_line + 4][30:40].strip()
        self.head_data['published_report'] = unit_data[file_line + 4][40:50].strip()
        self.head_data['urban'] = unit_data[file_line + 4][50:60].strip()
        
        if self.head_data['urban'] == 'URBANREFH':
            self.has_urban = True            
        
            self.head_data['subarea_1'] = unit_data[file_line + 5][0:10].strip()
            self.head_data['dplbar_1'] = unit_data[file_line + 5][10:20].strip()
            self.head_data['suburbext_1'] = unit_data[file_line + 5][20:30].strip()
            self.head_data['calibration_1'] = unit_data[file_line + 5][30:40].strip()
            self.head_data['subarea_2'] = unit_data[file_line + 6][0:10].strip()
            self.head_data['dplbar_2'] = unit_data[file_line + 6][10:20].strip()
            self.head_data['suburbext_2'] = unit_data[file_line + 6][20:30].strip()
            self.head_data['calibration_2'] = unit_data[file_line + 6][30:40].strip()
            self.head_data['subrunoff_2'] = unit_data[file_line + 6][40:50].strip()
            self.head_data['sewer_rp_2'] = unit_data[file_line + 6][50:60].strip()
            self.head_data['sewer_depth_2'] = unit_data[file_line + 6][60:70].strip()
            self.head_data['sewer_loss_vol_2'] = unit_data[file_line + 6][70:80].strip()
            self.head_data['subarea_3'] = unit_data[file_line + 7][0:10].strip()
            self.head_data['dplbar_3'] = unit_data[file_line + 7][10:20].strip()
            self.head_data['suburbext_3'] = unit_data[file_line + 7][20:30].strip()
            self.head_data['calibration_3'] = unit_data[file_line + 7][30:40].strip()
            self.head_data['subrunoff_3'] = unit_data[file_line + 7][40:50].strip()
        
        file_line += 5
        if self.has_urban: file_line += 3
        
        self.head_data['storm_area'] = unit_data[file_line][0:10].strip()
        self.head_data['storm_duration'] = unit_data[file_line][10:20].strip()
        self.head_data['sn_rate'] = unit_data[file_line][20:30].strip()
        self.head_data['rainfall_flag'] = unit_data[file_line+1][0:10].strip()
        self.head_data['arf_flag'] = unit_data[file_line+1][10:20].strip()
        self.head_data['rainfall_comment'] = unit_data[file_line+1][20:].strip()
        self.head_data['rainfall_od'] = unit_data[file_line+2][0:10].strip()
        self.head_data['return_period'] = unit_data[file_line+2][10:20].strip()
        self.head_data['arf'] = unit_data[file_line+2][20:30].strip()
        self.head_data['c'] = unit_data[file_line+2][30:40].strip()
        self.head_data['d1'] = unit_data[file_line+2][40:50].strip()
        self.head_data['d2'] = unit_data[file_line+2][50:60].strip()
        self.head_data['d3'] = unit_data[file_line+2][60:70].strip()
        self.head_data['e'] = unit_data[file_line+2][70:80].strip()
        self.head_data['f'] = unit_data[file_line+2][80:90].strip()
        self.head_data['rp_flag'] = unit_data[file_line+3][0:10].strip()
        self.head_data['scf_flag'] = unit_data[file_line+3][10:20].strip()
        self.head_data['scf'] = unit_data[file_line+3][20:30].strip()
        self.head_data['storm_rows'] = unit_data[file_line+4][0:10].strip()
        
        file_line = file_line + 5
        return file_line

        
    def _readStormData(self, unit_data, file_line):
        """
        """
        out_line = file_line + int(self.head_data['storm_rows'])
        for i in range(file_line, out_line):
            self.storm.append(unit_data[i][0:10].strip())
        
        return out_line
    
    
    def _readSuffix(self, unit_data, file_line):
        """
        """
        self.head_data['cmax_flag'] = unit_data[file_line][0:10].strip()
        self.head_data['cini_flag'] = unit_data[file_line][10:20].strip()
        self.head_data['alpha_flag'] = unit_data[file_line][20:30].strip()
        self.head_data['models_comment'] = unit_data[file_line][30:].strip()
        self.head_data['cm_dcf'] = unit_data[file_line+1][0:10].strip()
        self.head_data['cmax'] = unit_data[file_line+1][10:20].strip()
        self.head_data['cini'] = unit_data[file_line+1][20:30].strip()
        self.head_data['alpha'] = unit_data[file_line+1][30:40].strip()
        self.head_data['bfihost'] = unit_data[file_line+1][40:50].strip()
        self.head_data['uh_flag'] = unit_data[file_line+2][0:10].strip()
        self.head_data['tp_flag'] = unit_data[file_line+2][10:20].strip()
        self.head_data['up_flag'] = unit_data[file_line+2][20:30].strip()
        self.head_data['uk_flag'] = unit_data[file_line+2][30:40].strip()
        self.head_data['tp_dcf'] = unit_data[file_line+3][0:10].strip()
        self.head_data['tp0'] = unit_data[file_line+3][10:20].strip()
        self.head_data['tpt'] = unit_data[file_line+3][20:30].strip()
        self.head_data['dplbar'] = unit_data[file_line+3][30:40].strip()
        self.head_data['dpsbar'] = unit_data[file_line+3][40:50].strip()
        self.head_data['propwet'] = unit_data[file_line+3][50:60].strip()
        self.head_data['up'] = unit_data[file_line+3][60:70].strip()
        self.head_data['uk'] = unit_data[file_line+3][70:80].strip()
        self.head_data['uh_rows'] = unit_data[file_line+4][0:10].strip()
        self.head_data['bl_flag'] = unit_data[file_line+5][0:10].strip()
        self.head_data['br_flag'] = unit_data[file_line+5][10:20].strip()
        self.head_data['br0_flag'] = unit_data[file_line+5][20:30].strip()
        self.head_data['bl_dcf'] = unit_data[file_line+6][0:10].strip()
        self.head_data['bl'] = unit_data[file_line+6][10:20].strip()
        self.head_data['br_dcf'] = unit_data[file_line+6][20:30].strip()
        self.head_data['br'] = unit_data[file_line+6][30:40].strip()
        self.head_data['bf0'] = unit_data[file_line+6][40:50].strip()
        
        return file_line + 6


    def getData(self): 
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.
        
        Return:
            List of strings formated for writing to .dat file.
        """
        out_data = self._getHeadData()
        out_data.extend(self._getStormData()) 
        out_data.extend(self._getSuffix()) 
        
        return out_data
    
        
    def _getHeadData(self):
        """
        """
        out_data = []
        out_data.append('REFHBDY #revision#' + str(self.head_data['revision']) + ' ' + self.head_data['comment'])
        out_data.append(self.head_data['section_label'])

        out_data.append('{:>10}'.format(self.head_data['z']) + 
                        '{:>10}'.format(self.head_data['easting']) +
                        '{:>10}'.format(self.head_data['northing']))
        out_data.append('{:>10}'.format(self.head_data['time_delay']) + 
                        '{:>10}'.format(self.head_data['time_step']) +
                        '{:>10}'.format(self.head_data['bf_only']) +
                        '{:>10}'.format(self.head_data['sc_flag']) +
                        '{:>10}'.format(self.head_data['scale_factor']) +
                        '{:>10}'.format(self.head_data['hydrograph_mode']) +
                        '{:>10}'.format(self.head_data['hydrograph_scaling']) +
                        '{:>10}'.format(self.head_data['min_flow']))
        out_data.append('{:>10}'.format(self.head_data['catchment_area']) + 
                        '{:>10}'.format(self.head_data['saar']) +
                        '{:>10}'.format(self.head_data['urbext']) +
                        '{:>10}'.format(self.head_data['season']) +
                        '{:>10}'.format(self.head_data['published_report']) +
                        '{:>10}'.format(self.head_data['urban']))
        
        
        if self.has_urban:
            out_data.append('{:>10}'.format(self.head_data['subarea_1']) + 
                            '{:>10}'.format(self.head_data['dplbar_1']) +
                            '{:>10}'.format(self.head_data['suburbext_1']) +
                            '{:>10}'.format(self.head_data['calibration_1']))
            out_data.append('{:>10}'.format(self.head_data['subarea_2']) + 
                            '{:>10}'.format(self.head_data['dplbar_2']) +
                            '{:>10}'.format(self.head_data['suburbext_2']) +
                            '{:>10}'.format(self.head_data['calibration_2']) +
                            '{:>10}'.format(self.head_data['subrunoff_2']) +
                            '{:>10}'.format(self.head_data['sewer_rp_2']) +
                            '{:>10}'.format(self.head_data['sewer_depth_2']) +
                            '{:>10}'.format(self.head_data['sewer_loss_vol_2']))
            out_data.append('{:>10}'.format(self.head_data['subarea_3']) + 
                            '{:>10}'.format(self.head_data['dplbar_3']) +
                            '{:>10}'.format(self.head_data['suburbext_3']) +
                            '{:>10}'.format(self.head_data['calibration_3']) +
                            '{:>10}'.format(self.head_data['subrunoff_3']))
            
        
        out_data.append('{:>10}'.format(self.head_data['storm_area']) + 
                        '{:>10}'.format(self.head_data['storm_duration']) +
                        '{:>10}'.format(self.head_data['sn_rate']))
        out_data.append('{:>10}'.format(self.head_data['rainfall_flag']) + 
                        '{:>10}'.format(self.head_data['arf_flag']) +
                        self.head_data['rainfall_comment'])
        out_data.append('{:>10}'.format(self.head_data['rainfall_od']) + 
                        '{:>10}'.format(self.head_data['return_period']) +
                        '{:>10}'.format(self.head_data['arf']) +
                        '{:>10}'.format(self.head_data['c']) +
                        '{:>10}'.format(self.head_data['d1']) +
                        '{:>10}'.format(self.head_data['d2']) +
                        '{:>10}'.format(self.head_data['d3']) +
                        '{:>10}'.format(self.head_data['e']) +
                        '{:>10}'.format(self.head_data['f']))
        out_data.append('{:>10}'.format(self.head_data['rp_flag']) + 
                        '{:>10}'.format(self.head_data['scf_flag']) +
                        '{:>10}'.format(self.head_data['scf']))
        out_data.append('{:>10}'.format(self.head_data['storm_rows'])) 
            
        return out_data
     
        
    def _getStormData(self):
        """
        """
        out_data = []
        for line in self.storm:
            out_data.append('{:>10}'.format(line))
            
        return out_data
    
    
    def _getSuffix(self):
        """
        """
        out_data = []
        out_data.append('{:>10}'.format(self.head_data['cmax_flag']) + 
                        '{:>10}'.format(self.head_data['cini_flag']) +
                        '{:>10}'.format(self.head_data['alpha_flag']) +
                        self.head_data['models_comment'])
        out_data.append('{:>10}'.format(self.head_data['cm_dcf']) + 
                        '{:>10}'.format(self.head_data['cmax']) +
                        '{:>10}'.format(self.head_data['cini']) +
                        '{:>10}'.format(self.head_data['alpha']) +
                        '{:>10}'.format(self.head_data['bfihost']))
        out_data.append('{:>10}'.format(self.head_data['uh_flag']) + 
                        '{:>10}'.format(self.head_data['tp_flag']) +
                        '{:>10}'.format(self.head_data['up_flag']) +
                        '{:>10}'.format(self.head_data['uk_flag']))
        out_data.append('{:>10}'.format(self.head_data['tp_dcf']) +
                        '{:>10}'.format(self.head_data['tp0']) +
                        '{:>10}'.format(self.head_data['tpt']) +
                        '{:>10}'.format(self.head_data['dplbar']) +
                        '{:>10}'.format(self.head_data['dpsbar']) +
                        '{:>10}'.format(self.head_data['propwet']) +
                        '{:>10}'.format(self.head_data['up']) +
                        '{:>10}'.format(self.head_data['uk'])) 
        out_data.append('{:>10}'.format(self.head_data['uh_rows']))
        out_data.append('{:>10}'.format(self.head_data['bl_flag']) +
                        '{:>10}'.format(self.head_data['br_flag']) +
                        '{:>10}'.format(self.head_data['br0_flag']))
        out_data.append('{:>10}'.format(self.head_data['bl_dcf']) +
                        '{:>10}'.format(self.head_data['bl']) +
                        '{:>10}'.format(self.head_data['br_dcf']) +
                        '{:>10}'.format(self.head_data['br']) +
                        '{:>10}'.format(self.head_data['bf0']))
        
        return out_data
    
    
    
        