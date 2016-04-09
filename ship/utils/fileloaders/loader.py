"""

 Summary:
     Abstract base class that should be implemented by all file loading 
     classes in the API.
     
     Contains methods that help file loaders play nicely with the file loading
     factory and other parts of the API.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

class ALoader(object):
    """
    """
    
    def __init__(self):
        """
        """
        self.warning_store = []
    
    
    def loadFile(self, filepath, arg_dict={}):
        """Load the file at the given path
        
        Args:
            filepath (str): the file path to load.
            arg_dict={}(Dict): contains keyword referenced arguments needed by
                any of the loaders. E.g. the TuflowLoader can take some
                scenario values.
        
        Return:
        
        Raises:
            NotImplementedError: if subclass does not override this method.
        """
        raise NotImplementedError
        
    
    def _addWarning(self, title, msg):
        """Can be used to store non-deadly errors during load for easy lookup.
        
        The errors/warnings will be added to the warning_store list so that
        they can be passed on or interogated after the file has been loaded.
        
        This does not take the place of raising actual errors, it's just for
        noting anything that might be useful for the caller to know after 
        loading the file.
        
        Args:
            title (str): the title of the warning.
            msg (str): the message body of the warning.
        """
        self.warning_store.append((title, msg))
        
        
        
        
        