
from ship.utils.fileloaders import fileloader as fl
from ship.utils import filetools
# Used to accessing data stored in isis.datunits
from ship.fmp.datunits import ROW_DATA_TYPES as rdt

def trimRiverSections():
    """Deactivates all parts of isis/fmp river sections outside bankmarkers.
    
    Searches through all of the river sections in an isis/fmp model and sets
    deactivation markers at the location of all bankmarkers. I.e. where a 
    bankmarker was marked as left it will now have a deactivation marker there
    as well.
    
    Saves the updated file to disk with _Updated appended to the filename.
    """
    # Load the dat file into a new DatCollection object (isis_model)
    dat_path = r'C:\path\to\an\isis-fmp\datfile.dat'
    loader = fl.FileLoader()
    isis_model = loader.loadFile(dat_path)
    
    # Get the river sections from the model and loop through them
    rivers = isis_model.unitsByCategory('river')
    for river in rivers:
        
        # Get the bankmarker locations as a list for this river section
        bvals = river.row_data['main'].dataObjectAsList(rdt.BANKMARKER)
        
        # Get the DataObject for deactivation because we want to update it
        deactivation_data = river.row_data['main'].dataObjectAsList(rdt.DEACTIVATION)
        
        # Loop through the bankmarker values and each time we find one that's 
        # set (not False) we set the deactivation value at that index equal to 
        # the LEFT or RIGHT status of the bankmarker 
        for i, b in enumerate(bvals):
            if b == 'LEFT':
                deactivation_data.setValue('LEFT', i)
            elif b == 'RIGHT':
                deactivation_data.setValue('RIGHT', i)
    
    # Update the filename and write contents to disk
    isis_model.path_holder.filename = isis_model.path_holder.filename + '_Updated'
    out_path = isis_model.path_holder.absolutePath()
    isis_model.write(out_path)
    


if __name__ == '__main__':
    trimRiverSections()
    
    