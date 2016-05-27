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

import os

from ship.tuflow.tuflowfilepart import TuflowFile, TuflowFilePart
from ship.tuflow import FILEPART_TYPES as fpt
from ship.utils import utilfunctions as uf


class TuflowScenario(object):
    """
    """
    IF, ELSE, TUFLOW_PART, SCENARIO_PART, EVENT_PART = range(5)
    
    def __init__(self, if_type, values, hex_hash, order, comment, comment_char):
        """Constructor.
        
        Args:
            values(list): containing the different scenarios that are included
                in this class.
        """
        self.order = order
        self.if_type = if_type
        self.hex_hash = hex_hash
        self.values = values
        self.part_list = []
        self.comment = comment
        self.comment_char = comment_char
        self.has_endif = False
        self._first_tfp = None
        self.current_part_index = 0

    
    def addPartRef(self, ref_type, hex_hash):
        """Add a reference to a command that's included in this scenario.
        
        Args:
            ref_type(int): indicating if the ref in a TuflowFilePart or another
                TuflowScenario. Use the class constants TUFLOW_PART or SCENARIO_PART.
            hex_hash(str): hash code of a TuflowFilePart to include.
        """
        self.part_list.append([ref_type, hex_hash])
        if ref_type == TuflowScenario.TUFLOW_PART:
            if self._first_tfp is None:
                self._first_tfp = hex_hash
                
                
    def getTuflowFilePartRefs(self):
        """Return all TuflowFileParts referenced by this scenario object.
        
        Return:
            list - containing TuflowFilePart hash codes, if any found.
        """
        refs = []
        for p in self.part_list:
            if p[0] == TuflowScenario.TUFLOW_PART:
                refs.append(p[1])
        
        return refs
    
    
    def getOpeningStatement(self):
        """Get the opeing statement from this scenario block.
        
        All scenarios have an opening statement of some form. This could be
        either 'IF SCENARIO == X', 'ELSE IF SCENARIO == X', or 'ELSE'. This
        function will return the appropriate str based on the setup of this
        scenario object.
        
        Return:
            str - containing the appropriate opening statement.
        """
        output = []
        if self.values[0] == 'ELSE':
            output.append('ELSE')
        else:
            if self.if_type == TuflowScenario.IF:
                output.append('IF SCENARIO ==')
            else:
                output.append('ELSE IF SCENARIO ==')
            
            val = []
            for v in self.values:
                val.append(v)
            val = ' | '.join(val) 
            output.append(val)
        
        if not self.comment_char == '':
            output.append(self.comment_char + ' ' + self.comment + '\n')
        else:
            output.append('\n')
        
        output = ' '.join(output)
        return output
    
    
    def getClosingStatement(self):
        """Get the closing statement from this scenario block.
        
        Some will have an 'END IF' and some won't. E.g. an if statement followed
        by an if-else will not because it's close is the same as the opening
        statement of the else section.
        
        Return:
            str - containing an 'END IF' or ''.
        """
        if self.has_endif:
            return 'END IF\n'
        else:
            return ''


class TuflowEvent(object):
    """
    """
    DEFINE, END = range(2)
    
    def __init__(self, if_type, value, hex_hash, order, comment, comment_char):
        """Constructor.
        
        Args:
            values(list): containing the different scenarios that are included
                in this class.
        """
        self.order = order
        self.if_type = if_type
        self.hex_hash = hex_hash
        self.values = [value]
        self.part_list = []
        self.comment = comment
        self.comment_char = comment_char
        self.current_part_index = 0

    
    def addPartRef(self, hex_hash):
        """Add a reference to a command that's included in this scenario.
        
        Args:
            hex_hash(str): hash code of a TuflowFilePart to include.
        """
        self.part_list.append(hex_hash)
                
                
    def getTuflowFilePartRefs(self):
        """Return all TuflowFileParts referenced by this scenario object.
        
        Return:
            list - containing TuflowFilePart hash codes, if any found.
        """
        refs = []
        for p in self.part_list:
            refs.append(p)
        
        return refs
    
    
    def getOpeningStatement(self):
        """Get the opeing statement from this scenario block.
        
        All scenarios have an opening statement of some form. This could be
        either 'IF SCENARIO == X', 'ELSE IF SCENARIO == X', or 'ELSE'. This
        function will return the appropriate str based on the setup of this
        scenario object.
        
        Return:
            str - containing the appropriate opening statement.
        """
        output = 'DEFINE EVENT == ' + self.values[0] + self.comment_char + self.comment + '\n'
        return output
    
    
    def getClosingStatement(self):
        """Get the closing statement from this scenario block.
        
        Return:
            str - containing an 'END DEFINE'.
        """
        return 'END DEFINE\n'

    
    

class TuflowModelFile(object):
    """ Contains data pertaining to TUFLOW model files.
    
    The main model files that are loaded by TUFLOW, e.g. Tcf, Tgc, etc, have
    their meta data and references to their contents stored in this class.
    
    Contains a list denoting the order of the file and any lines that are 
    either comments or not recognised by the loader.
    
    Other, known, file commands are stored in the approproate object (instances
    of :class: 'TuflowFilePart') and their hash key is stored in this list.
        
    See Also:
        :class: 'TuflowFile <ship.tuflow.tuflowfilepart.TuflowFile>'
        :module: 'tuflowfilepart <ship.tuflow.tuflowfilepart>'
    """

    def __init__(self, category, hex_hash, parent_hash):
        """Constructor.

        Checks if the path to the file is absolute. If it doesn't it converts
        it. If the absolute path doesn't exist an error will be raised.

        Args:
            category (str): a type variable denoting which form of model file this
                is. E.g. tcf, tgc, etc.
            hex_hash(str): a unique hexidecimal hash code.
            parent_hash(str): the unique code of the file that created this
                model file (e.g. if this was a tgc referenced by a tcf the
                parent would be the tcf file).
        """
        self.TYPE = category
        self.hex_hash = hex_hash
        self.parent_hash = parent_hash
        self.contents = []
        self.scenarios = []
        self.events = []


    def getPrintableContents(self, has_estry_auto):
        """Get the printable contents from each file referenced by this class.
        
        Args:
            model_file(self.file): file to retrive the contents from.
            
        Results:
            List containing the entries in the model_file.
        """
        output = []
        skip_lines = []
        
        def getPrintableFilepart(f, indent):
            """
            """
            # If there's piped files
            if isinstance(f, TuflowFile) and not f.child_hash is None:
                out_line = []
                has_children = True
                out_line.append(f.getPrintableContents())
                
                # Keep looping through until there are no more piped files
                child_count = 1
                while has_children:
                    if not f.child_hash is None:
                        f = self.contents[i + child_count][1]
                        out_line.append(f.getPrintableContents())
                        skip_lines.append(i + child_count)
                        child_count += 1
                    else:
                        output.append(indent + ' | '.join(out_line) + '\n')
                        has_children = False
                    
            else:
                output.append(indent + f.getPrintableContents() + '\n')
        
        ##
        # END INNER FUNCTION
        ##
        
        scen_stack = uf.LoadStack()
        scenarios = [s for s in sorted(self.scenarios)]
        evt_stack = uf.LoadStack()
        events = [e for e in sorted(self.events)]
        indent_spacing = 0
        indent = ''
        
        '''Read the order of the contents in the model file.
        [0] = the type of file part: MODEL, COMMENT, GIS, etc
        [1] = the hex_hash of the file part
        [2] = the comment contents (or None if it's not a comment section
        '''
        for i, entry in enumerate(self.contents, 0):
            
            line_type = entry[0]
            if i in skip_lines: continue

            if line_type == fpt.COMMENT:
                output.append(''.join(entry[1]))
            else:
                
                if entry[0] == fpt.SCENARIO:
                    scen_stack.add(scenarios.pop(0))
                    output.append(indent + scen_stack.peek().getOpeningStatement())
                    indent_spacing += 4
                    indent = ''.join([' '] * indent_spacing)
                
                elif entry[0] == fpt.SCENARIO_END:
                    indent_spacing -= 4
                    indent = ''.join([' '] * indent_spacing)
                    output.append(indent + scen_stack.peek().getClosingStatement())
                    scen_stack.pop()
                
                elif entry[0] == fpt.EVENT:
                    evt_stack.add(events.pop(0))
                    output.append(indent + evt_stack.peek().getOpeningStatement())
                    indent_spacing += 4
                    indent = ''.join([' '] * indent_spacing)
                
                elif entry[0] == fpt.EVENT_END:
                    indent_spacing -= 4
                    indent = ''.join([' '] * indent_spacing)
                    output.append(indent + evt_stack.peek().getClosingStatement())
                    evt_stack.pop()
                
                else: 
                    f = entry[1]
                    if f.category == 'ecf':
                        if has_estry_auto:
                            temp = ' '.join([f.command, 'Auto !', f.comment])
                            output.append(indent + temp)
                    else:
                        getPrintableFilepart(f, indent)
                    
        
        return output
    
    
    def getSEVariables(self, scenario=True, event=True):
        """Returns all of the scenario variables in this file.
        
        Tuflow control files can use if-else logic on scenario setups. These are
        variables, separated by pipes, that can be given to a model at run time
        to specifiy which files and variables to use.
        
        Return:
            list - all of the variables found in this control file.
        """
        vals = {'scenario': [], 'event': []}
        for s in self.scenarios:
            for v in s.values:
                if not v in vals and not v == 'ELSE':
                    vals['scenario'].append(v)
        
        for e in self.events:
            for v in e.values:
                if not v in vals:
                    vals['event'].append(v)
        
        
        return vals
    
    
    def getHashesBySE(self, se_vals, filepart_type=None):
        """Get the hash codes for all TuflowFileParts in scenario/events.
        
        Returns the hex_hash values for all of the TuflowFilePart's held by
        this object that are within the TuflowScenario and TuflowEvent classes
        defined by the values in se_vals.
        
        The actual operation of this function is a little contrary to what
        you might expect. Instead of getting the values inside the required
        scenarios it gets the values that are in all of the other scenarios and
        then discounts them when comparing against all of the hex_hash values
        in this classes self.contents. This is done becuase not all values are
        inside scenarios and events, i.e. they are global and always used. This
        approach is a lot simpler than most of the other methods of dealing
        with this.
        
        Args:
        
        
        Return:
        
        
        """
        k = se_vals.keys()
        if not 'scenario' in k and not 'event' in k: raise KeyError

        has_scen = 'scenario' in se_vals.keys()
        has_evt = 'event' in se_vals.keys()
        hashes = []
        miss_hashes = []
        for s in self.scenarios:
            scen_vals = s.values
            for v in scen_vals:
                if has_scen and v in se_vals['scenario']: 
                    miss_hashes.extend(s.getTuflowFilePartRefs())
                else:
                    hashes.extend(s.getTuflowFilePartRefs())
        
        # Need this in case a scenario has more than one argument. 
        hashes = [h for h in hashes if not h in miss_hashes]

        
        miss_hashes = []
        for e in self.events:
            evt_vals = e.values
            for v in evt_vals:
                if has_evt and v in se_vals['event']:
                    continue
                else:
                    hashes.extend(e.getTuflowFilePartRefs())
        
        out_hashes = []
        for c in self.contents:
            if isinstance(c[1], TuflowFilePart):
                if not c[1].hex_hash in hashes:
                    if filepart_type is None or c[0] == filepart_type:
                        out_hashes.append(c[1].hex_hash)
                    
        return out_hashes
    
    
    def getContentsBySE(self, se_vals, filepart_type=None):
        """Returns a list of TuflowFilePart's based on the given scenario_vals.
        
        Any TuflowFilePart that is within a TuflowScenario or TuflowEvent with 
        the values set to those provided in the list will be returned.
        
        The vals dict must contain at least one list as a value under a key of
        either 'scenario' or 'event'. Or it may contain both. E.g.
            :: vals = {'scenario': [s1, s2], 'event': [e1, e2]}
        
        Args:
            vals(dict{list, list}): lists of str's representing scenario and 
                event variables in this control file.
        
        Return:
            list - containing TuflowFilePart's that meet the criteris of the
                given scenario and event vals.
        
        Raises:
            KeyError - if neither 'scenario' or 'event' are keys in vals.
        """
        
        hashes = self.getHashesBySE(se_vals, filepart_type)
        file_parts = []
        for c in self.contents:
            if not isinstance(c[1], TuflowFilePart):
                continue
            if not filepart_type is None and not c[0] == filepart_type:
                continue
            if c[1].hex_hash in hashes:
                file_parts.append(c[1])
            
        return file_parts

    
    def addContent(self, line_type, filepart): 
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
        """
        self.contents.append([line_type, filepart])
    
    
    def addScenario(self, scenario):
        """Add a TuflowScenario.
        
        TuflowScenario's are used to store information about if else clauses in
        the control files, such as the logic terms of the clause and which 
        TuflowFileParts are within the clause.
        
        Args:
            scenario(TuflowScenario):
        """
        self.scenarios.append(scenario)
    
    
    def addEvent(self, event):
        """Add a TuflowEvent.
        
        TuflowEvents's are used to store information about define-event clauses 
        in the control files, such as which TuflowFileParts are within the clause.
        
        Args:
            event(TuflowEvent):
        """
        self.events.append(event)
 
    
    def getEntryByHash(self, hex_hash):
        """Return the TuflowFilePart referenced by a particular hash code. 
        
        Args:
            hex_hash(str): the hash code.
        
        Return:
            TuflowFilePart
            
        Raises:
            KeyError - if no part was found with the given hash code.
            
        """
        for c in self.contents:
            if not isinstance(c[1], TuflowFilePart): continue
            if c[1].hex_hash == hex_hash:
                return c[1]
        else:
            raise KeyError ("No entry found with hex_hash: " + hex_hash)
    
    
    def testExists(self):
        """Tests each file to see if it exists.
        
        Returns:
            list - containing tuple's (filename, absolute path) of any files
                that do not exist.
        """
        failed = []
        for c in self.contents:
            if isinstance(c[1], TuflowFile):
                p = c[1].getAbsolutePath()
                if c[0] == fpt.RESULT:
                    continue
                else:
                    if not os.path.exists(p):
                        failed.append([c[1].getFileNameAndExtension(), 
                                       os.path.normpath(p)])
        
        return failed
    
    
    def getFiles(self, file_type=None, extensions=[], include_results=True,
                 se_vals=None):
        """Get the TuflowFile objects referenced by this object.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing TuflowFile objects.
        """
        hashes = []
        if not se_vals is None:
            hashes = self.getHashesBySE(se_vals, file_type)
        output = []
        for c in self.contents:
            if isinstance(c[1], TuflowFile):
                
                if not file_type is None and not c[0] == file_type: 
                    continue
                elif not se_vals is None and not c[1].hex_hash in hashes:
                    continue
                elif not include_results and c[0] == fpt.RESULT:
                    continue
                else:
                    if extensions and not c[1].extension in extensions:
                        continue
                    output.append(c[1])
        
        return output
    
    
    def getFileNames(self, file_type=None, extensions=[], with_extension=True, 
                     all_types=False, include_results=True, se_vals=None):
        """Get all of the file names for TuflowFile object in this class.
        
        This is a convenience method. It calls the getFiles method and extracts
        the file name from the TuflowFile's.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            with_extension=True(bool): if True the file extension will be 
                included in the return values.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing file names as strings.
        """
        files = self.getFiles(file_type, extensions, include_results, se_vals)
        
        output = []
        if with_extension:
            if all_types:
                for f in files:
                    
                    output.extend(f.getFileNameAndExtensionAllTypes())
            else:
                output = [f.getFileNameAndExtension() for f in files]
        else:
            output = [f.file_name for f in files]
        
        return output
    
    
    def getAbsolutePaths(self, file_type=None, extension=None, all_types=False,
                         se_vals=None):
        """Get all of the absolute paths for TuflowFile objects in this class.
        
        This is a convenience method. It calls the getFiles method and extracts
        the absolute path from the TuflowFile's.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing absolute paths as strings.
        """
        files = self.getFiles(file_type, extension, se_vals=se_vals)
        files = [f.getAbsolutePath(all_types=all_types) for f in files]

        return files
            

    def getRelativePaths(self, file_type=None, extension=None, all_types=False,
                         se_vals=None):
        """Get all of the relative paths for TuflowFile objects in this class.
        
        This is a convenience method. It calls the getFiles method and extracts
        the relative path from the TuflowFile's.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing relative paths as strings.
        """
        files = self.getFiles(file_type, extension, se_vals=se_vals)
        files = [f.getRelativePath(all_types=all_types) for f in files]

        return files
    
    
    def getVariables(self, se_vals=None):
        """Get all of the ModelVariable's referenced by this object.
        
        Return:
            list - of ModelVariable's.
        """
        output = []
        if not se_vals is None:
            output = self.getContentsBySE(se_vals, fpt.VARIABLE)
        else:
            for c in self.contents:
                if c[0] == fpt.VARIABLE:
                    output.append(c[1])
        
        return output
    
    
    


    
    
    