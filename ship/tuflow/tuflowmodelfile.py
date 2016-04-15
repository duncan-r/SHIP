"""

 Summary:
     Container for the main tuflow model files (tcf/tgc/etc).
     
     This class is used to store the order of items in the file and any data
     that is not understood by the tuflowloader e.g. commented sections and
     components of the file that are not specifically listed.
     
     If does not store the data directly, just the hash codes for the file
     parts so that they can be cross referenced against the 
     TuflowModel.file_parts dictionary.
     
     The ModelFileEntry class is also kept in this module. This provides simple 
     access to main variables held by the TuflowFilePart objects.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

from ship.tuflow.tuflowfilepart import SomeFile

class ModelFileEntry(object):
    
    def __init__(self, filepart, part_type, hex_hash):
        self.filepart = filepart
        self.hex_hash = hex_hash
        self.part_type = part_type
        self.file_name = None

        if isinstance(self.filepart, SomeFile):
            self.file_name = self.filepart.file_name
            

    def isSomeFile(self):
        """
        """
        return isinstance(self.filepart, SomeFile)
    
        

class TuflowModelFile(object):
    """ Contains data pertaining to TUFLOW model files.
    
    The main model files that are loaded by TUFLOW, e.g. Tcf, Tgc, etc, have
    their meta data and references to their contents stored in this class.
    
    Contains a list denoting the order of the file and any lines that are 
    either comments or not recognised by the loader.
    
    Other, known, file commands are stored in the approproate object (instances
    of :class: 'TuflowFilePart') and their hash key is stored in this list.
        
    See Also:
        :class: 'SomeFile <ship.tuflow.tuflowfilepart.SomeFile>'
        :module: 'tuflowfilepart <ship.tuflow.tuflowfilepart>'
    """

    def __init__(self, line_type, hex_hash):
        """Constructor.

        Checks if the path to the file is absolute. If it doesn't it converts
        it. If the absolute path doesn't exist an error will be raised.

        Args:
            type (str): a type variable denoting which form of model file this
                is. E.g. tcf, tgc, etc.
        """
        self.TYPE = line_type
        self.hex_hash = hex_hash
        self.content_order = []

    
    def addContent(self, line_type, hex_hash, unknown_contents=None):
        """Add an entry to the content_order list.
        
        Entries are added in order so that the order can be maintained.
        
        This could be either a reference (hash code) for a 
        :class:'TuflowFilePart' type object or actual contents. The actual 
        contents are sent if the line is a comment or isn't known by the
        loader.
        
        Args:
            line_type (int): denotes the code to store the entry under. This is
                one of the constants in :class:'TuflowModel' (GIS, MODEL, etc).
            hex_hash (hex): the unique hex value of the line hash used to 
                identify all parts of the tuflow model.
            unknown_contents (str): Optional - this will be handed in if the
                loader cannot work out what to do with it. This way it can go
                back out the same as it came in.
        """
#         self.content_order.append(modelfile_entry)
        if unknown_contents is None:
            self.content_order.append([line_type, hex_hash])
        else:
            self.content_order.append([line_type, hex_hash, unknown_contents])
 
     
    def getHashCategory(self, line_type=None, include_comments=False):
        """Returns the hex hash codes for all the objects of type.
         
        Args:
            line_type (int): denotes the code find. This is one of the constants 
            in :class:'TuflowModel' (GIS, MODEL, etc).
         
        Returns:
            list - all of the hash codes in category type.
        """
        if line_type is None: 
            if include_comments:
                results = [c[1] for c in self.content_order]
            else:
                results = [c[1] for c in self.content_order if not len(c) > 2] 
        else:
            results = [c[1] for c in self.content_order if c[0] is line_type]
        return results