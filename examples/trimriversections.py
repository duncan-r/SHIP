import os
from ship.utils.fileloaders import fileloader as fl
from ship.utils import filetools
# Used to accessing data stored in isis.datunits
from ship.isis.datunits import ROW_DATA_TYPES as rdt


def trimRiverSections():
    """Deactivates all parts of isis/fmp river sections outside bankmarkers.
    
    Searches through all of the river sections in an isis/fmp model and sets
    deactivation markers at the location of all bankmarkers. I.e. where a 
    bankmarker was marked as left it will now have a deactivation marker there
    as well.
    
    Saves the updated file to disk with _Updated appended to the filename.
    """
    # Load the dat file into a new DatCollection object (isis_model)
    dat_file = r'C:\path\to\an\isis-fmp\datfile.dat'
    loader = fl.FileLoader()
    isis_model = loader.loadFile(dat_file)
    
     # Get the river sections from the model and loop through them
    rivers = isis_model.getUnitsByCategory('River')
    for river in rivers:
        
        # Get the bankmarker locations as a list for this river section
        bvals = river.getRowDataAsList(rdt.BANKMARKER)
        
        # Get the DataObject for deactivation because we want to update it
        deactivation_data = river.getRowDataObject(rdt.DEACTIVATION)
        
        # Loop through the bankmarker values and each time we find one that it 
        # set (not False) we that the value at that index equal to it's LEFT or
        # RIGHT status.
        for i, b in enumerate(bvals):
            if b == 'LEFT':
                deactivation_data.setValue('LEFT', i)
            elif b == 'RIGHT':
                deactivation_data.setValue('RIGHT', i)
    
    
    # Update and get the filename of the isis_model
    fname = os.path.basename(dat_file)
    ext = os.path.splitext(dat_file)[1]
    new_dat = fname + '_Updated' + ext
    isis_model.path_holder.setFileName(new_dat, has_extension=True, keep_extension=True)
    dat_path = isis_model.path_holder.getAbsolutePath()

    # Get the contents of the updated isis model
    contents = isis_model.getPrintableContents()
    
    # Write the new isis model to file
    filetools.writeFile(contents, dat_path)
    


if __name__ == '__main__':
    trimRiverSections()
    
    