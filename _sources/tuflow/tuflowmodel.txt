.. _tuflowmodel-top:

***********
TuflowModel
***********

TuflowModel is main container class for all the components of a Tuflow model.
When you load a .tcf file with FileLoader it will return an instance of
TuflowModel.

##################
Loading .tcf files
##################

Like all files in the SHIP library .tcf files can be loaded with the
FileLoader class::

   from ship.utils.fileloaders.fileloader import FileLoader
   
   tcf_path = "C:/path/to/a/tcffile.tcf"
   loader = FileLoader()
   tuflow = loader.loadFile(tcf_path)

After loading a TuflowModel it is usually a good idea to check that it managed
to load all of the linked control files. It will not automatically fail and
raise an IOError if some of the .tgc, .tbc, .tef, .ecf, or .trd files could not
be found. This approach means that you can run it once and be aware of all 
missing files. To check that the model was fully loaded without issues use::

   # Returns a list
   missing_files = tuflow.missing_model_files
   
   # If the model loaded without problems this will print an empty list
   # If not it will print a list containing the filename's of all the control
   # files that could not be loaded
   print (missing_files)
   

########
Overview
########

The TuflowModel class itself does not provide a lot of functionality. Primarily
it is a container for for the ControlFile objects and a number of classes and
variables that are required globally. These are:

   - **user_variables(UserVariables)**: a class containing a the scenario values,
     event values, and user defined variables set in the control files.
   - **bc_event(dict)**: contains the currently set BC Event variables (i.e.
     'BC Event Name', 'BC Event Text' and 'BC Event Source'.
   - **root(str)**: the directory that the loaded .tcf file is in. As Tuflow models
     generally use relative paths between files, this is used to derive the
     absolute paths of the different components.
     

###########
Data Access
###########

Generally the main component of the TuflowModel used is the control_files
dict. You can use this to access the different ControlFiles includes in the
currently loaded model::

   # Individually access the ControlFiles objects
   # Note that if a particular type of file is not included in the model it
   # will raise a KeyError
   tgc = tuflow.control_files['TGC']
   tef = tuflow.control_files['TEF']

   # Loop through all of the loaded control file types
   for key, control in tuflow.control_files.items():
      print (key)
      # ... do something with ControlFile

There are not a lot of methods in the TuflowModel. One that is of interest
is the checkPathsExist(). This is just a wrapper for the same function in the
ControlFile's, but allows for a quick check that all files referenced by the
ControlFile's exist.


.. _tuflowmodel-uservariables:

##############
User Variables
##############

The UserVariables class is in the ship.tuflow.tuflowmodel.py module. It is
used to store all user defined variables in a tuflow model. This includes the
scenario and event logic values, whether set within the control files or from
the batchfile/command line (just like Tuflow, if any scenario/event values are
provided as an argument to the loaded they will supersede all found in the
control files). It also includes any variables set in the control files 
using the 'Set somevariables == anumber' syntax.

It stores all of these in three dicts:

   - **scenario(dict)**: containing a dict of TuflowModelVariable's
   - **event(dict)**: containing a dict of TuflowModelVariable's
   - **variables(dict)**: containing a dict of TuflowUserVariable's
   
The keys to access the TuflowModelVariable or TuflowUserVariable objects are 
the variable names. You can either access the dict's directly or use the
get() method, which takes a key and a 'vtype' value: either 'scenario', 'event',
or None (default is None - if None it will look in the variables dict).

There are two main methods that you will probably use a lot of:

   - seValsToDict()
   - variablesToDict()

The first will return a dict in the format::

   se_vals = {
       'scenario': {
          's1': 'scen1', 's2': 'scen2'
        },
       'event': {
          'e1': 'evt1', 'e2': '5'
       }
    }   
             
This dict is accepted by most of the methods in the ControlFile class, to limit
the returned values to those inside the current event. The contents of this
dict will be the currently active scenario and event logic.

The second method will return a dict in the format::

   variables = {
      's1': 'scen1',
      's2': 'scen2',
      'e1': 'evt1',
      'e2': 5,
      'myfirstvar': 2.5,
      'anothervar': 9,
   }

These are all of the currently set user variables in the model. You will notice
that it also includes the scenario and event variables (continuing the example
from above). This is because Tuflow treats the scenario and event value as
variables as well, so you can do 'Cell Size == <<e2>>' if you want or 
'Cell Size == <<myfirstvar>>' it doesn't make any difference.

   
   
   
   