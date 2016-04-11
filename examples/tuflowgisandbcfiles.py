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
# Used for function args in tuflow model
from ship.tuflow.tuflowmodel import FilesFilter  


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
    
    # Create a filter object to set specific function arg status with 
    # additional arguments set to defaults
    f = FilesFilter(content_type=tuflow_model.GIS, no_duplicates=True)
    
    # Get file names and absolute paths of all gis files referenced by the model
    gis_files = tuflow_model.getFileNames(f)
    gis_paths = tuflow_model.getAbsolutePaths(f)
    combined = dict(zip(gis_files, gis_paths))
    
    # Get the data files objs referenced by the model.
    # These are files that point to additional data (tmf, bcdbase, 1d_xs, etc)
    # In this case we want the the object itself, not just the filename, so 
    # we use the getContents method instead
    bc_combined = []
    data_objs = tuflow_model.getContents(content_type=tuflow_model.DATA, no_duplicates=True)
    
    # Loop through the data_objs and extract the names and file sources for 
    # each of the BC Database type files
    for data in data_objs:
        if data.command.upper() == 'BC DATABASE':
            
            bc = dfl.loadDataFile(data)
            names = bc.getDataEntryAsList(bc.keys.NAME)
            sources = bc.getDataEntryAsList(bc.keys.SOURCE)
            bc_combined.append((data.getFileNameAndExtension(), dict(zip(names, sources))))
        
    print 'GIS files in model:'
    for g in gis_files: print g
    print '\nBC Database files in model:'
    for b in bc_combined:
        print b[0]
        for x in b[1].values(): print x



if __name__ == '__main__':
    tuflowFileExample()
