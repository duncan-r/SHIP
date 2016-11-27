.. _unitdescriptions-top:

*****************
Unit Descriptions
*****************

An overview of the standard data in the AUnit type classes is put here for
reference. It includes:
   
   - a summary of the head_data keys and input types.
   - a list of row_data keys.

There is support for RefhUnit in the library. However the head_data entires are
so numerous that it would take for ever to put them all down here. For more 
information on what is available in the RefhUnit please see
ship.fmp.datunits.refhunit
   
**Note** 
Where types are specified in head_data, prefaced with dt, dt means::
   
   ship.datastructures.DATA_TYPES as dt

Where types are specified in row_data, prefaced with rdt, rdt means::
   
   ship.fmp.ROW_DATA_TYPES as rdt


#########
RiverUnit
#########

Type and Category
=================

unit_type = 'river'
unit_category = 'river'

ic_labels
=========
self.name

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='spill1', data_type=dt.STRING
   * key='spill2', data_type=dt.STRING
   * key='spill2', data_type=dt.STRING
   * key='lateral1', data_type=dt.STRING
   * key='lateral2', data_type=dt.STRING
   * key='lateral3', data_type=dt.STRING
   * key='lateral4', data_type=dt.STRING
   * key='distance', data_type=dt.FLOAT, dps=3
   * key='slope', data_type=dt.FLOAT, dps=4
   * key='density', data_type=dt.INT


Row Data
========

**row_data['main']**
   * DataObject=FloatData, key=rdt.CHAINAGE, no_of_dps=3
   * DataObject=FloatData, key=rdt.ELEVATION, no_of_dps=3)
   * DataObject=FloatData, key=rdt.ROUGHNESS, default=0.039, no_of_dps=3
   * DataObject=SymbolData, symbol=*, key=rdt.PANEL_MARKER, default=False
   * DataObject=FloatData, key=rdt.RPL, default=1.000, no_of_dps=3
   * DataObject=do.ConstantData, rdt.BANKMARKER, choices=('LEFT', 'RIGHT', 'BED'), default=''
   * DataObject=FloatData, key=rdt.EASTING, default=0.0, no_of_dps=2
   * DataObject=FloatData, key=rdt.NORTHING, default=0.0, no_of_dps=2
   * DataObject=ConstantData, rdt.DEACTIVATION, choices=('LEFT', 'RIGHT'), default=''
   * DataObject=StringData, key=rdt.SPECIAL, default='~'
     # Default == '~' means to ignore formatting and apply '' when value is None
            
            
##############
BridgeUnitArch
##############

Type and Category
=================

unit_type = 'bridge'
unit_category = 'arch'

ic_labels
=========
self.name, self.name_ds

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='remote_us', data_type=dt.STRING
   * key='remote_ds', data_type=dt.STRING
   * key='roughness_type', data_type=dt.CONSTANT, choices=('MANNING',)
   * key='calibration_coef', data_type=dt.FLOAT, dps=3
   * key='skew_angle', data_type=dt.FLOAT, dps=3
   * key='width', data_type=dt.FLOAT, dps=3
   * key='dual_distance', data_type=dt.FLOAT, dps=3
   * key='num_of_orifices', data_type=dt.INT
   * key='orifice_flag', data_type=dt.CONSTANT, choices=('', 'ORIFICE')
   * key='op_lower', data_type=dt.FLOAT, dps=3
   * key='op_upper', data_type=dt.FLOAT, dps=3
   * key='op_cd', data_type=dt.FLOAT, dps=3


Row Data
========
            
**row_data['main']**
   * DataObject=FloatData, key=rdt.CHAINAGE, no_of_dps=3
   * DataObject=FloatData, key=rdt.ELEVATION, no_of_dps=3)
   * DataObject=FloatData, key=rdt.ROUGHNESS, no_of_dps=3
   * DataObject=ConstantData, rdt.EMBANKMENT, choices=('L', 'R'), default=''

**row_data['opening']**
   * DataObject=FloatData, key=rdt.OPEN_START, no_of_dps=3
   * DataObject=FloatData, key=rdt.OPEN_END, no_of_dps=3
   * DataObject=FloatData, key=rdt.SPRINGING_LEVEL, no_of_dps=3
   * DataObject=FloatData, key=rdt.SOFFIT_LEVEL, no_of_dps=3


###############
BridgeUnitUsbpr
###############

Type and Category
=================

unit_type = 'bridge'
unit_category = 'usbpr'

ic_labels
=========
self.name, self.name_ds

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='remote_us', data_type=dt.STRING
   * key='remote_ds', data_type=dt.STRING
   * key='roughness_type', data_type=dt.CONSTANT, choices=('MANNING',)
   * key='calibration_coef', data_type=dt.FLOAT, dps=3
   * key='skew_angle', data_type=dt.FLOAT, dps=3
   * key='width', data_type=dt.FLOAT, dps=3
   * key='dual_distance', data_type=dt.FLOAT, dps=3
   * key='num_of_orifices', data_type=dt.INT
   * key='orifice_flag', data_type=dt.CONSTANT, choices=('', 'ORIFICE')
   * key='op_lower', data_type=dt.FLOAT, dps=3
   * key='op_upper', data_type=dt.FLOAT, dps=3
   * key='op_cd', data_type=dt.FLOAT, dps=3
   * key='abutment_type', data_type=dt.CONSTANT, choices=('1', '2', '3')
   * key='num_of_piers', data_type=dt.INT
   * key='pier_shape', data_type=dt.CONSTANT, choices=('FLAT', 'ARCH')
   * key='pier_shape_2', data_type=dt.CONSTANT, choices=('FLAT', 'ARCH')allow_blank=True),
   * key='pier_calibration_coef', data_type=dt.FLOAT, dps=3, allow_blank=True
   * key='abutment_align', data_type=dt.CONSTANT, choices=('ALIGNED', 'SKEW')


Row Data
========

**row_data['main']**
   * DataObject=FloatData, key=rdt.CHAINAGE, no_of_dps=3
   * DataObject=FloatData, key=rdt.ELEVATION, no_of_dps=3)
   * DataObject=FloatData, key=rdt.ROUGHNESS, no_of_dps=3
   * DataObject=ConstantData, rdt.EMBANKMENT, choices=('L', 'R'), default=''

**row_data['opening']**
   * DataObject=FloatData, key=rdt.OPEN_START, no_of_dps=3
   * DataObject=FloatData, key=rdt.OPEN_END, no_of_dps=3
   * DataObject=FloatData, key=rdt.SPRINGING_LEVEL, no_of_dps=3
   * DataObject=FloatData, key=rdt.SOFFIT_LEVEL, no_of_dps=3

**row_data['culvert']**
   * DataObject=FloatData, key=rdt.INVERT, no_of_dps=3)
   * DataObject=FloatData, key=rdt.SOFFIT, no_of_dps=3)
   * DataObject=FloatData, key=rdt.AREA, no_of_dps=3
   * DataObject=FloatData, key=rdt.CD_PART, no_of_dps=3
   * DataObject=FloatData, key=rdt.CD_FULL, no_of_dps=3
   * DataObject=FloatData, key=rdt.DROWNING, no_of_dps=3


#####################
InitialConditionsUnit
#####################

Type and Category
=================

unit_type = 'initial_conditions'
unit_category = 'initial_conditions'

head_data contents
==================

None


Row Data
========

**row_data['main']**
   * DataObject=StringData, key=rdt.LABEL
   * DataObject=StringData, key=rdt.QMARK, default='y'
   * DataObject=FloatData, key=rdt.FLOW, default=0.000, no_of_dps=3
   * DataObject=FloatData, key=rdt.STAGE, default=0.000, no_of_dps=3
   * DataObject=FloatData, key=rdt.FROUDE_NO, default=0.000, no_of_dps=3
   * DataObject=FloatData, key=rdt.VELOCITY, default=0.000, no_of_dps=3
   * DataObject=FloatData, key=rdt.UMODE, default=0.000, no_of_dps=3
   * DataObject=FloatData, key=rdt.USTATE, default=0.000, no_of_dps=3
   * DataObject=FloatData, key=rdt.ELEVATION, default=0.000, no_of_dps=3


#########
SpillUnit
#########

Type and Category
=================

unit_type = 'spill'
unit_category = 'spill'

ic_labels
=========
self.name, self.name_ds

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='weir_coef', data_type=dt.FLOAT, dps=3
   * key='modular_limit', data_type=dt.FLOAT, dps=3


Row Data
========

**row_data['main'] - rdt.CHAINAGE must increase*
   * DataObject=FloatData, key=rdt.CHAINAGE, no_of_dps=3 
   * DataObject=FloatData, key=rdt.ELEVATION, no_of_dps=3
   * DataObject=FloatData, key=rdt.EASTING, no_of_dps=2, default=0.00
   * DataObject=FloatData, key=rdt.NORTHING, no_of_dps=2, default=0.00
            
            
            
###########
OrificeUnit
###########

FloodReliefUnit and OutfallUnit have the same setup as OrificeUnit, including
the same unit_category (orifice). Although they differ in unit_type:

   - FloodReliefUnit unit_type == 'flood_relief'
   - OutfallUnit unit_type == 'outfall'

Type and Category
=================

unit_type = 'orifice'
unit_category = 'orifice'

ic_labels
=========
self.name, self.name_ds

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='type', data_type=dt.CONSTANT, choices=('OPEN', 'FLAPPED',
   * key='invert_level', data_type=dt.FLOAT, dps=3
   * key='soffit_level', data_type=dt.FLOAT, dps=3
   * key='bore_area', data_type=dt.FLOAT, dps=3
   * key='us_sill_level', data_type=dt.FLOAT, dps=3
   * key='ds_sill_level', data_type=dt.FLOAT, dps=3
   * key='shape', data_type=dt.CONSTANT, choices=('RECTANGLE', 'CIRCULAR',
   * key='weir_flow', data_type=dt.FLOAT, dps=3
   * key='surcharged_flow', data_type=dt.FLOAT, dps=3
   * key='modular_limit', data_type=dt.FLOAT, dps=3


Row Data
========
            
None


############
JunctionUnit
############

Note that JunctionUnit.head_data containes one non-HeadDataItem entry for names.
I may update this to use HeadDataItem in the future, but for now, just to be
confusing the value is a list.

Type and Category
=================

unit_type = 'junction'
unit_category = 'junction'

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='type', data_type=dt.CONSTANT, choices=('OPEN', 'ENERGY')
   * key='names': []


Row Data
========

None


###############
InterpolateUnit
###############

Type and Category
=================

unit_type = 'interpolate'
unit_category = 'interpolate'

ic_labels
=========
self.name

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='spill1', data_type=dt.STRING
   * key='spill2', data_type=dt.STRING
   * key='lateral1', data_type=dt.STRING
   * key='lateral2', data_type=dt.STRING
   * key='lateral3', data_type=dt.STRING
   * key='lateral4', data_type=dt.STRING
   * key='distance', data_type=dt.FLOAT, dps=3
   * key='easting', data_type=dt.FLOAT, dps=3
   * key='northing', data_type=dt.FLOAT, dps=3


Row Data
========

None



#########
HtbdyUnit
#########

Type and Category
=================

unit_type = 'htbdy'
unit_category = 'boundary_ds'

ic_labels
=========
self.name

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='multiplier', data_type=dt.FLOAT, dps=3
   * key='time_units', data_type=dt.CONSTANT, choices=time_units
   * key='extending_method', data_type=dt.CONSTANT, choices=('EXTEND', 'NOEXTEND', 'REPEAT',
   * key='interpolation', data_type=dt.CONSTANT, choices=('LINEAR', 'SPLINE',

Where time_units are::

        time_units = (
            'SECONDS', 'MINUTES', 'HOURS', 'DAYS', 'WEEKS', 'FORTNIGHTS',
            'LUNAR MONTHS', 'MONTHS', 'QUARTERS', 'YEARS', 'DECADES', 'USER SET',
        )

Row Data
========

**row_data['main']**
   * DataObject=FloatData, key=rdt.ELEVATION, no_of_dps=3
   * DataObject=FloatData, key=rdt.TIME, no_of_dps=3



################
CulvertInletUnit
################

Type and Category
=================

unit_type = 'culvert_inlet'
unit_category = 'culvert'

ic_labels
=========
self.name

head_data contents
==================

   * key='comment', data_type=dt.STRING
   * key='k', data_type=dt.FLOAT, dps=4
   * key='m', data_type=dt.FLOAT, dps=3
   * key='c', data_type=dt.FLOAT, dps=4
   * key='y', data_type=dt.FLOAT, dps=3
   * key='ki', data_type=dt.FLOAT, dps=3
   * key='conduit_type', data_type=dt.CONSTANT, choices=('A', 'B', 'C')
   * key='screen_width', data_type=dt.FLOAT, dps=3
   * key='bar_proportion', data_type=dt.FLOAT, dps=3
   * key='debris_proportion', data_type=dt.FLOAT, dps=3
   * key='loss_coef', data_type=dt.FLOAT, dps=3
   * key='trashscreen_height', data_type=dt.FLOAT, dps=3
   * key='headloss_type', data_type=dt.CONSTANT, choices=('STATIC', 'TOTAL')
   * key='reverse_flow_model', data_type=dt.CONSTANT, choices=('CALCULATED', 'ZERO')


Row Data
========

None
