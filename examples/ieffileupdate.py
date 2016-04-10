"""
    Summary:
        Example use of the isis package to update file paths in an .ief file
        and save the ief file under a new name.
    
    Author:  
        Duncan Runnacles

    Created:  
        01 Apr 2016

    Copyright:  
        Duncan Runnacles 2016

    TODO:

    Updates:

"""

import os
from ship.utils.fileloaders import fileloader as fl
# Contains functions for updating file paths and reading/writing files
from ship.utils import filetools


def iefExample():
    """update some key file paths in an ief file.
    
    Updates the .dat file, .ief file, and results file paths referenced by
    the ief file and save it under a new ief file name. 
    """
    # Load the tuflow model with a tcf file
    ief_file = r'C:\path\to\an\isis\ieffile.tcf'
    loader = fl.FileLoader()
    ief = loader.loadFile(ief_file)
    
    # Get the referenced fmp .dat and .tcf files
    dat_path = ief.getValue('Datafile')
    tcf_path = ief.getValue('2DFile')
    results_path = ief.getValue('Results')
    
    # Update the dat, results and tcf file names
    root, ext = os.path.splitext(dat_path)
    new_dat = root + '_Updated' + ext
    root, ext = os.path.splitext(results_path)
    new_results = root + '_Updated' + ext
    root, ext = os.path.splitext(tcf_path)
    new_tcf = root + '_Updated' + ext
    ief.setValue('Datafile', new_dat)
    ief.setValue('Results', new_results)
    ief.setValue('2DFile', new_tcf)
    
    # Update and get the filename of the ief
    fname = os.path.basename(ief_file)
    ext = os.path.splitext(ief_file)[1]
    new_ief = fname + '_Updated' + ext
    ief.path_holder.setFileName(new_ief, has_extension=True, keep_extension=True)
    ief_path = ief.path_holder.getAbsolutePath()

    # Get the contents of the updated ief
    contents = ief.getPrintableContents()
    
    # Write the new ief to file
    filetools.writeFile(contents, ief_path)
    

if __name__ == '__main__':
    iefExample()
    
    