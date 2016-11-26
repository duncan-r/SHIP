"""
    Summary:
        Example use of the tuflow package to identify all of the gis files
        and boundary condition database files referenced by a tuflow model.
    
    Author:  
        Duncan Runnacles

    Created:  
        01 Apr 2016

    Copyright:  
        Duncan Runnacles 2016

    TODO:

    Updates:

"""

from ship.utils.fileloaders import fileloader as fl
# Used for loading tuflow data files
from ship.tuflow.data_files import datafileloader as dfl
# Enum for accessing TuflowFilePart types (GIS, MODEL, RESULT, VARIABLE, DATA)
from ship.tuflow import FILEPART_TYPES as ft

def tuflowFileExample():
    """Find all gis and bc database files referenced by a tuflow model.
    
    Uses a .tcf file to load a tuflow model and find all of the gis files and
    BC Database files referenced by it. Also identifies any additional files
    referenced by the BC Database files.
    """
    # Load the tuflow model with a tcf file
    tcf_file = r'C:\path\to\a\tuflow\tcffile.tcf'
    loader = fl.FileLoader()
    tuflow_model = loader.loadFile(tcf_file)
    
    data_files = []
    names = []
    paths = []
    # Loop through the different control files fetching the GIS and DATA files.
    for ckey, cfile in tuflow_model.control_files.items():

        # Get file names and absolute paths of all gis files referenced by the model
        gis_files = cfile.files(filepart_type=ft.GIS)
        for g in gis_files:
            names.append(g.filenameAndExtension())
            paths.append(g.absolutePath())

        # Get the data files objs referenced by the model.
        # These are files that point to additional data (tmf, bcdbase, 1d_xs, etc)
        data_files = cfile.files(filepart_type=ft.DATA)


    gis_combined = dict(zip(names, paths))
    
    
    # Loop through the data_objs and extract the names and file sources for 
    # each of the BC Database type files
    bc_combined = []
    for data in data_files:
        if data.command.upper() == 'BC DATABASE':
            
            bc = dfl.loadDataFile(data)
            names = bc.dataObjectAsList(bc.keys.NAME)
            sources = bc.dataObjectAsList(bc.keys.SOURCE)
            bc_combined.append((data.filenameAndExtension(), dict(zip(names, sources))))
        
    print ('GIS files in model:')
    for name, path in gis_combined.items(): 
        print (name + ':\n' + path)
    print ('\nBC Database files in model:')
    for b in bc_combined:
        print (b[0])
        for x in b[1].values(): 
            print (x)



if __name__ == '__main__':
    tuflowFileExample()
