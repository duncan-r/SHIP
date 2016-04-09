Example Usage
======================

.. highlight:: python
	:linenos:

ISIS / Flood Modeller Pro
#########################

Loading an Isis/Flood Modeller Pro .dat file
********************************************

Loading a .dat file is simple:
::
	# Import tmac_tools_lib API modules
	from tmac_tools_lib.utils.fileloaders.fileloader import FileLoader

	# Create a file loader object
	loader = FileLoader()
	
	# Load the .dat file
	isis_units = loader.loadFile(r'c:\path\to\model.dat')

	
Accessing the model data
************************

If you then want to access some of the data in a River Unit for example:
::
	# Need to import the river class and data types
	from tmac_tools_lib.isis.datunits import RiverUnit as ru
	from tmac_tools_lib.isis.datunits import ROW_DATA_TYPES

	# Get the river units
	rivers = isis_model.getUnitsByCategory('River')

        # Loop through the river units
        for river in rivers:

            # Get the river mannings values
            n_vals = river.getRowDataAsList(ROW_DATA_TYPES.MANNINGS)

Which will loop through all of the River Units in the model and grab the Manning's n values stored in them. Although it 
won't actually do anything with it yet.

Amending model data
*******************

To update some model data instead of just obtaining it you can do:
::
    # Import tmac_tools_lib API modules
    from tmac_tools_lib.utils.fileloaders.fileloader import FileLoader

    # Need to import the river class
    from tmac_tools_lib.isis.datunits import RiverUnit as ru
    # Alternitivley you could always just import the datunits module
    #from tmac_tools_lib.isis import datunits as dats
	from tmac_tools_lib.isis.datunits import ROW_DATA_TYPES

    # Create a .dat file loader object
    loader = FileLoader()

    # Load the .dat file
    isis_model = loader.loadFile(r'c:\path\to\model.dat')

    # Get the river units
    rivers = isis_model.getUnitsByCategory('River')

    # Loop through the river units
    for river in rivers:

        # Get the mannings data object from the river unit
        n_vals = river.getRowDataObject(ROW_DATA_TYPES.MANNINGS)

        # Update all of the roughness values
        for i in range(0, n_vals.record_length):
            val = n_vals.getValue(i)
            n_vals.setValue((val*1.2), 		

    # When you're done; create a new file name
    new_name = units.path_holder.file_name
    new_name = new_name + '_Rgh+20%'
    units.path_holder.setFileName(new_name)

    # and save everything to file
    from tmac_tools_lib.utils import filetools
    dat_contents = isis_model.getPrintableUnits()
    filetools.writeFile(dat_contents, isis_model.path_holder.getAbsPath())

Which should give you a new .dat file with all the roughness values increased by 20%.


TUFLOW
######################


