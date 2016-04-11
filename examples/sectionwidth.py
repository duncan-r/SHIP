"""
    Summary:
        Example use of the isis package to calculate the full cross section
        width and active cross section width of river and bridge sections in 
        an isis/fmp .dat file.
    
    Author:  
        Duncan Runnacles

    Created:  
        01 Apr 2016

    Copyright:  
        Duncan Runnacles 2016

    TODO:

    Updates:

"""

import math
from ship.utils.fileloaders import fileloader as fl
from ship.isis.datunits import ROW_DATA_TYPES as rdt


def crossSectionWidth():
    """Calculate river and bridge cross section widths.
    
    Populates a dictionary with the river unit name, full cross section width
    and active cross section width for all river units in a isis/fmp .dat model
    file. Then gets the width of all the bridge units in the model.
    
    Finally prints a summary of the calculations to the console.
    """
    # Load the dat file into a new DatCollection object
    dat_file = r'C:\path\to\an\isis-fmp\datfile.dat'
    loader = fl.FileLoader()
    isis_model = loader.loadFile(dat_file)

    section_details = []

    # Get the river sections from the model and loop through them
    rivers = isis_model.getUnitsByCategory('River')
    for river in rivers:
        
        # Get the width and deactivation values form the river section
        xvals = river.getRowDataAsList(rdt.CHAINAGE)
        dvals = river.getRowDataAsList(rdt.DEACTIVATION)
        
        x_start = xvals[0]
        x_end = xvals[-1]
        has_deactivation = False
        
        # loop through the section width values, check where any deactivation
        # markers are and set the active width start and end variables accordingly
        for i, x in enumerate(xvals, 0):
            if dvals[i] == 'LEFT':
                x_start = x
                has_deactivation = True
            if dvals[i] == 'RIGHT':
                x_end = x
                has_deactivation = True
        
        full_width = math.fabs(xvals[-1] - xvals[0])
        active_width = math.fabs(x_end - x_start)
        
        section_details.append({'Name': river.name, 'Unit': river.CATEGORY, 
                                'Full Width': full_width,
                                'Active Width': active_width, 
                                'Has deactivation': has_deactivation}
                              )
    
    # Get the widths of the bridges too
    bridges = isis_model.getUnitsByCategory('Bridge')
    for bridge in bridges:
        xvals = bridge.getRowDataAsList(rdt.CHAINAGE)
        
        full_width = math.fabs(xvals[-1] - xvals[0])
        
        # Note that we set the 'Unit' value with UNIT_TYPE rather than CATEGORY
        # this time. It means that we will get what type of bridge it is
        # (Arch/Usbpr) rather than just that it's a bridge.
        section_details.append({'Name': bridge.name, 'Unit': bridge.UNIT_TYPE, 
                                'Full Width': full_width,
                                'Active Width': full_width, 
                                'Has deactivation': False}
                              )
    
    for section in section_details:
        print section



if __name__ == '__main__':
    crossSectionWidth()
