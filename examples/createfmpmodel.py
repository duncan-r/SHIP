"""
    Summary:
        Example use of the fmp package to create a new empty DatCollection 
        object and add some units to it.
        
        In this example the data added to the new units is hardcoded into the
        script. In reality you would probably parse it from .csv files or
        similar.
    
    Author:  
        Duncan Runnacles

    Created:  
        28 Nov 2016

    Copyright:  
        Duncan Runnacles 2016

    TODO:

    Updates:

"""

from ship.fmp.datcollection import DatCollection
from ship.fmp.fmpunitfactory import FmpUnitFactory as factory
from ship.fmp.datunits import ROW_DATA_TYPES as rdt

def createModelExample():
    """Create a new FMP model and add a couple of river units to it.
    
    Generates a new DatCollection and adds some units with data to it. Note that
    the 'initialisedDat()' method that's used is a classmethod of DatCollection.
    It will automatically create the AUnit types that are required by Flood
    Modeller. These include:
        - HeaderUnit: the data at the top of the file.
        - InitialConditionsUnit: the data at/near the bottom of the file that
            stores all of the initial conditions for nodes.
            
    It also adds a CommentUnit as the first unit.
    """
    
    # Create some data to prepopulate our RiverUnit's with. You can do it this
    # way (as one big dict)
    riv1_data = {
        'name': 'riv1',
        'head_data': {'distance': 10.5},
        'row_data': {
            'main': [
                {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.035},
                {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 7.0, rdt.ROUGHNESS: 0.035},
                {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 4.0, rdt.ROUGHNESS: 0.035},
                {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 4.0, rdt.ROUGHNESS: 0.035},
                {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 7.0, rdt.ROUGHNESS: 0.035},
                {rdt.CHAINAGE: 10.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.035},
            ],
        }
    }
    river1 = factory.createUnit('river', **riv1_data)
    
    # Or this way (separate variables)
    head_data = {'distance': 12.0}
    row_data = {
        'main': [
            {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 9.0, rdt.ROUGHNESS: 0.035},
            {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 6.0, rdt.ROUGHNESS: 0.035},
            {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 3.0, rdt.ROUGHNESS: 0.035},
            {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 3.0, rdt.ROUGHNESS: 0.035},
            {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 6.0, rdt.ROUGHNESS: 0.035},
            {rdt.CHAINAGE: 10.0, rdt.ELEVATION: 9.0, rdt.ROUGHNESS: 0.035},
        ],
    }
    river2 = factory.createUnit('river', name='riv2', head_data=head_data,
                                row_data=row_data)
    
    
    # The path we'll save our new model to.
    new_path = "C:/path/to/fmp/model.dat"
    
    '''
    Then create a new DatCollection and give it units river1 and river2.
    
    Note that you can provide kwargs to be used when adding the units under
    the keyword 'unit_kwargs'. An example is given with the unit_kw setup
    below. When this is supplied you must provide either some kwargs, or an 
    empty dict as a placeholder for each entry in units. The kwargs at 
    unit_kwargs index i will be used for the unit at units index i.
    '''
    unit_kw = [{}, 
        {
            'ics': {rdt.FLOW: 3.0, rdt.STAGE: 5.0, rdt.ELEVATION: 4.5}
        }
    ]
    dat = DatCollection.initialisedDat(new_path, units=[river1, river2],
                                       unit_kwargs=unit_kw)
    
    '''
    A different approach.
    
    You can also creat a unit with it's constructor and populate the rows after
    if you prefer. It's then added to the DatCollection
    '''
    # You'll need to import the unit specific module
    from ship.fmp.datunits import riverunit as riv
    
    # Instantiate the unit (if name is not given it will get a default)
    river3 = riv.RiverUnit(name='riv3')
    
    # Set some head_data
    river3.head_data['distance'].value = 15.0
    
    # Create some row_data and add it to the unit
    rows = [ 
        {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 8.0, rdt.ROUGHNESS: 0.035},
        {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 5.0, rdt.ROUGHNESS: 0.035},
        {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 2.0, rdt.ROUGHNESS: 0.035},
        {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 2.0, rdt.ROUGHNESS: 0.035},
        {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 5.0, rdt.ROUGHNESS: 0.035},
        {rdt.CHAINAGE: 10.0, rdt.ELEVATION: 8.0, rdt.ROUGHNESS: 0.035},
    ]
    for r in rows:
        river3.addRow(r)
    
    '''
    If you call addUnit without an index it will be appended to the end of the
    units. Here we find the index of river2 and put river3 there. This will 
    push river2 back up by one (i.e. order is now river1, river3, river2).
    Note that we can hand initial conditions in as a kwarg here like before.
    '''
    riv2_index = dat.index(river2)
    dat.addUnit(river3, index=riv2_index, ics={rdt.FLOW: 3.0, 
                                               rdt.STAGE: 5.0,
                                               rdt.ELEVATION: 4.5})
    
    # Write the new fmp .dat file to disk
    dat.write()
    
    
    '''
    It's worth noting that if you're not worried about populating the units with
    data from the outset it can be a very simple operation.
    '''
    # Just get a blank DatCollection with no units (except header and ics)
    new_path2 = "C:/path/to/fmp/model2.dat"
    dat2 = DatCollection.initialisedDat(new_path2)
    dat2.write()
    
    
    '''
    Final go.
    
    Create a new DatCollection but add a few empty units to it
    The units below will be added to the DatCollection in the order of the list.
    '''
    units = [
        factory.createUnit('refh', name='riv1'),
        factory.createUnit('river', name='riv2'),
        factory.createUnit('river', name='riv3'),
        factory.createUnit('arch', name='brg1'),
        factory.createUnit('river', name='riv4'),
        factory.createUnit('river', name='riv5'),
        factory.createUnit('htbdy', name='htbdy'),
    ]
    new_path3 = "C:/path/to/fmp/model3.dat"
    dat3 = DatCollection.initialisedDat(new_path3, units=units)
    dat3.write()
    
    
    
    