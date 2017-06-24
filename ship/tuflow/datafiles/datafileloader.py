"""

 Summary:
     Deals with loading all data from ADataObject type files.
     
     This process can get quite messy so it seems sensible to have a separate
     factory to deal with it.
     
     See Also:
         ADataObject, TmfDataObject, TmfCsvDataObject, DcDataObject

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:
     Need to add a subfile loader for the materials csv file loader.
     
     This module needs some cleaning up still. There is quite a bit of repeated
     code around that could be pulled out into module level functions and used
     by all of the loader.

 Updates:


"""

from __future__ import unicode_literals

import csv
import os

# ship modules
from ship.datastructures.rowdatacollection import RowDataCollection
from ship.datastructures import dataobject as do
from ship.tuflow.tuflowfilepart import DataFile, GisFile, TuflowFile
from ship.tuflow.datafiles import datafileobject as dataobj
from ship.utils import filetools
from ship.utils import utilfunctions as uuf
from ship.utils.dbfread import DBF

import logging
logger = logging.getLogger(__name__)


def loadDataFile(datafile, args_dict={}):
    """Factory function for creating DataFileObject type objects.

    Loads the contents of the DataFileObject based on the composition of the
    given object and returns the newly created DataFileObject of that type.

    The args_dict is a dict of key-value pairs where the key represents a 
    placeholder used within one of the data files and the value reprents the
    variables that should be used to replace that value. This is common in
    bc_dbase file for instance where '__event__' may be used as a place holder
    with BC Event Text and BC Event Name used in the control files to define
    what should be used. Other options are the use of scenario and event 
    definitions. Within these BC Event Source can be defined to associate 
    certain placeholders with values e.g.::

        Define Event == 8hr
            BC Event Source == ~DUR~ | 8hr
            BC Database == ..\bc_dbase\my_bcdbase.csv
        End Define

    These are stored in the tuflow model when loaded and can be passed when 
    loading data files to use.

    Args:
        datafile(TuflowFile): FilePart to create the DataFileObject from.
        args_dict={}(dict): This is a dictionary of keywords and associated 
            values that can be used to identify and replace placeholders in the
            source file names or column names within data files. NOTE CURRENTLY
            NOT USED. 

    Return:
        DataFileObject: of type identified from the composition of the given
            TuflowFile object.

    Note:
        The args_dict is CURRENTLY NOT USED, but will be supported soon.

    See Also:
        TuflowFile
        DataFileObject
    """
    if not isinstance(datafile, TuflowFile):
        raise AttributeError('datafile is not an instance of TuflowFile')

    command = datafile.command.upper()
    if command == 'READ MI TABLE LINKS':
        if not isinstance(datafile, GisFile):
            raise AttributeError('datafile is not an instance of GisFile')

        row_data, comments = readXsFile(datafile)
        xs = dataobj.XsDataObject(row_data, datafile, comments, args_dict)
        return xs

    # Anything else must be a DataFile instance
    if not isinstance(datafile, DataFile):
        raise AttributeError('datafile is not an instance of DataFile')

    # List containing checks for the file command and them any different file
    # types that are dealt with under that command.
    if command == 'READ MATERIALS FILE':
        if datafile.extension.lower() == 'tmf':
            row_data, comments = readTmfFile(datafile)
            tmf = dataobj.TmfDataObject(row_data, datafile, comments, args_dict)
            return tmf

        if datafile.extension.lower() == 'csv':
            row_data, comments, subfile_details = readMatCsvFile(datafile, args_dict)
            mat = dataobj.MatCsvDataObject(row_data, datafile, comments)

            # Load any subfiles
            for path, header_list in subfile_details.iteritems():
                mat.addSubfile(readMatSubfile(datafile, path, header_list, args_dict))

            return mat

    elif command == 'BC DATABASE':
        row_data, comments = readBcFile(datafile, args_dict)
        bc = dataobj.BcDataObject(row_data, datafile, comments, args_dict)
        return bc

    else:
        logger.error('Command type (%s) with extension (%s) is not currently supported'
                     % (datafile.command, datafile.extension))
        raise ValueError('Command type (%s) with extension (%s) is not currently supported'
                         % (datafile.command, datafile.extension))


def readXsFile(datafile):
    """Loads the contents of the estry 1d_xs file reference by datafile.
    """
    value_separator = ','
    comment_types = []
    xs_enum = dataobj.XsEnum()

    def loadShapeFile(file_path, row_collection):
        """Loads cross section data from Shapefile .dbf format.

        Uses the dbfreader library.
        """
        try:
            table = DBF(file_path, load=True)
        except IOError:
            logger.error('Unable to load file at: ' + file_path)
            raise IOError('Unable to load file at: ' + file_path)

        for i, t in enumerate(table.records):
            count = 0
            for entry in t.values():
                row_collection._addValue(count, entry)
                count += 1

            # Need to catch the fact that skew does not exist in some versions.
            if count < len(xs_enum.ITERABLE):
                logger.info('1d_xs does not have skew column - adding default value')
                for k in range(count, len(xs_enum.ITERABLE)):
                    row_collection._addValue(k)

#             print t['Source'] + ' : ' + t['Type'] + ' : ' + t['Column_1']
            row_collection._addValue('row_no', i)

        return row_collection

    def loadMapinfoFile(file_path, row_collection):
        """Load cross section data from Mapinfo .mid format.
        """
        try:
            with open(file_path, 'rb') as csv_file:
                csv_file = csv.reader(csv_file)
                for i, row in enumerate(csv_file):

                    for j, entry in enumerate(row):
                        row_collection._addValue(j, entry)

                    # Need to catch the fact that skew does not exist in some versions.
                    if len(row) < len(xs_enum.ITERABLE):
                        logger.info('1d_xs does not have skew column - adding deafult value')
                        for k in range(len(row), len(xs_enum.ITERABLE)):
                            row_collection._addValue(k)

    #                 print row[0] + ' : ' + row[1] + ' : ' + row[3]
                    row_collection._addValue('row_no', i)

        except IOError:
            logger.error('Unable to load file at: ' + file_path)
            raise IOError('Unable to load file at: ' + file_path)

        return row_collection

    def setupRowCollection():
        """Setup the RowDataCollection for loading the data into.
        """
        # First entry doesn't want to have a comma in front when formatting.
        row_collection = RowDataCollection()
        types = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]

        # Do the first entry separately because it has a different format string
        row_collection.addToCollection(do.StringData(0, format_str='{0}', default=''))
        for i, t in enumerate(types, 1):
            if t == 0:
                row_collection.addToCollection(do.StringData(i, format_str=', {0}', default=''))
            else:
                row_collection.addToCollection(do.FloatData(i, format_str=', {0}', no_of_dps=3, default=0.00))

        # Add a couple of extra rows to the row_collection for tracking the
        # data in the file.
        row_collection.addToCollection(do.IntData('row_no'))

        return row_collection

    '''
        Main Section
    '''
    row_collection = setupRowCollection()
    ext = datafile.extension.lower()
    file_path = datafile.absolutePath()

    # If we're loading a MapInfo mid/mif file
    if ext == 'mif' or ext == 'mid':

        if ext == 'mif':
            dir, name = os.path.split(file_path)
            name, ext = os.path.splitext(name)
            file_path = os.path.join(dir, name + '.mid')

        row_collection = loadMapinfoFile(file_path, row_collection)

    # If we're loading a Shapefile
    elif ext == 'shp' or ext == 'dbf':

        if ext == 'shp':
            dir, name = os.path.split(file_path)
            name, ext = os.path.splitext(name)
            file_path = os.path.join(dir, name + '.dbf')

        row_collection = loadShapeFile(file_path, row_collection)

    else:
        logger.warning('Invalid file extension for XS type in file: ' + datafile.filenameAndExtension())
        raise ValueError('Invalid file extension for XS type in file: ' + datafile.filenameAndExtension())

    # Always return an empty comments list because there will never be any.
    return row_collection, []


def readBcFile(datafile, args_dict={}):
    """Loads the contents of the BC Database file refernced by datafile.

    Loads the data from the file referenced by the given TuflowFile object into
    a :class:'rowdatacollection' and a list of comment only lines.

    Args:
        datafile(TuflowFile): TuflowFile object with file details.

    Return:
        tuple: rowdatacollection, comment_lines(list).

    See Also:
        :class:'rowdatacollection'.
    """
    value_seperator = ','
    comment_types = ['#', '!']
    bc_enum = dataobj.BcEnum()
    bc_event_data = args_dict

    def _checkHeaders(row, required_headers):
        """Checks that any required headers can be found.

        Reviews the headers in the header row of the csv file to ensure that
        any specifically needed named column headers exist.

        Args:
            row(list): columns headers.
            required_headers(list): column names that must be included.

        Return:
            list if some headers not found of False otherwise.
        """
        # Check what we have in the header row
        head_check = True
        for r in required_headers:
            if not r in row:
                head_check = False
        if not head_check:
            logger.warning('Required header (' + r + ') not' +
                           'found in file: ' + path)
        return head_check

    def _loadHeadData(row, row_collection, required_headers):
        """Loads the column header data.

        Adds the file defined names for the headers to the rowdatacollection.

        Args:
            row(list): containing the row data.
            row_collection(rowdatacollection): for updating.
            required_headers(list): column names that must exist.

        Return:
            rowdatacollection: updated with header row details.
        """
        row_length = len(row)
        head_check = _checkHeaders(row, required_headers)
        for i, v in enumerate(bc_enum.ITERABLE):
            if i < row_length:
                row_collection._addValue('actual_header', row[i])

        return row_collection

    def _loadRowData(row, row_count, row_collection):
        """Loads the data in a specific row of the file.

        Args:
            row(list): containing the row data.
            row_count(int): the current row number.
            required_headers(list): column names that must exist.

        Return:
            rowdatacollection: updated with header row details.
        """
        if '!' in row[-1] or '#' in row[-1]:
            row_collection._addValue('comment', row[-1])

        # Add the row data in the order that it appears in the file
        # from left to right.
        for i in bc_enum.ITERABLE:
            if i < len(row):
                row_collection._addValue(i, row[i])

        return row_collection

    # Initialise the RowDataOjectCollection object with currect setup
    row_collection = RowDataCollection()
    for i, val in enumerate(bc_enum.ITERABLE):
        if i == 0:
            row_collection.addToCollection(do.StringData(i, format_str='{0}', default=''))
        else:
            row_collection.addToCollection(do.StringData(i, format_str=', {0}', default=''))

    row_collection.addToCollection(do.StringData('actual_header', format_str=', {0}', default=''), index=0)
    row_collection.addToCollection(do.IntData('row_no', format_str=None, default=''))

    path = datafile.absolutePath()
    required_headers = ['Name', 'Source']
    try:
        logger.info('Loading data file contents from disc - %s' % (path))
        with open(path, 'rU') as csv_file:
            csv_file = csv.reader(csv_file)

            # Stores the comments found in the file
            comment_lines = []
            first_data_line = False
            row_count = 0
            # Loop through the contents list loaded from file line-by-line.
            for i, line in enumerate(csv_file, 0):

                comment = hasCommentOnlyLine(''.join(line), comment_types)
                if comment or comment == '':
                    comment_lines.append(comment)

                # If we have a line that isn't a comment or a blank then it is going
                # to contain materials entries.
                else:
                    # First non-comment is the headers
                    if first_data_line == False:
                        first_data_line = True
                        row_collection = _loadHeadData(line, row_collection, required_headers)
                    else:
                        row_collection = _loadRowData(line, i, row_collection)
                        row_collection._addValue('row_no', row_count)
                        row_count += 1

                    comment_lines.append(None)

    except IOError:
        logger.warning('Cannot load file - IOError')
        raise IOError('Cannot load file at: ' + path)

    # Just need to reset the has_changed variable because it will have been
    # set to True while loading everything in.
    for i in range(0, len(bc_enum.ITERABLE)):
        row_collection.dataObject(i).has_changed = False

    return row_collection, comment_lines


def readMatCsvFile(datafile, args_dict={}):
    """Loads the contents of the Materials CSV file referenced by datafile.

    Loads the data from the file referenced by the given TuflowFile object into
    a :class:'rowdatacollection' and a list of comment only lines.

    Args:
        datafile(TuflowFile): TuflowFile object with file details.

    Return:
        tuple: rowdatacollection, comment_lines(list).

    See Also:
        :class:'rowdatacollection'.
    """
    value_seperator = ','
    comment_types = ['#', '!']
    csv_enum = dataobj.MatCsvEnum()
    subfile_details = {}

    def _loadHeadData(row, row_collection):
        """
        """
        new_row = [None] * 12

        if '!' in row[-1] or '#' in row[-1]:
            row_collection._addValue('comment', row[-1])

        new_row[0] = row[0]
        new_row[1] = row[1]
        new_row[9] = row[2]
        new_row[11] = row[3]

        row_length = len(new_row)
        for i, v in enumerate(new_row):
            if i < row_length:
                row_collection._addValue('actual_header', new_row[i])

        return row_collection

    def _disectEntry(col_no, entry, new_row):
        """Breaks the row values into the appropriate object values.

        The materials file can have Excel style sub-values. i.e. it can have
        seperate columns defined within a bigger one. This function will break
        those values down into a format usable by the values initiated in the
        rowdatacollection.

        Args:
            col_no(int): the current column number.
            entry(string): the value of the current column.
            new_row(list): the row values to update.

        Return:
            list containing the updated row values.

        Note:
            This isn't very nice. Need to clean it up and find a better, safer
            way of dealing with breaking the row data up. It may be excess work
            but perhaps creating an xml converter could work quite will and
            make dealing with the file a bit easier?
        """
        made_change = False

        # Put in ID and Hazard as normal
        if col_no == 0:
            new_row[0] = entry
        elif col_no == 11:
            new_row[11] = entry
        # Possible break up Manning's entry further
        elif col_no == 1:
            # See if there's more than one value in the Manning's category.
            splitval = entry.split(',')

            # If there is and it's numeric then it's a single value for 'n'
            if len(splitval) == 1:
                if uuf.isNumeric(splitval[0]):
                    new_row[1] = splitval[0]

                # Otherwise it's a filename. These can be further separated
                # into two column headers to read from the sub files.
                else:
                    strsplit = splitval[0].split('|')
                    if len(strsplit) == 1:
                        subfile_details[strsplit[0].strip()] = []
                        new_row[6] = strsplit[0].strip()
                    elif len(strsplit) == 2:
                        subfile_details[strsplit[0]] = [strsplit[1].strip()]
                        new_row[6] = strsplit[0].strip()
                        new_row[7] = strsplit[1].strip()
                    else:
                        subfile_details[strsplit[0]] = [strsplit[1].strip(), strsplit[2].strip()]
                        new_row[6] = strsplit[0].strip()
                        new_row[7] = strsplit[1].strip()
                        new_row[8] = strsplit[2].strip()

            # If there's more than one value then it must be the Manning's
            # depth curve values (N1, Y1, N2, Y2).
            else:
                new_row[2] = splitval[0]
                new_row[3] = splitval[1]
                new_row[4] = splitval[2]
                new_row[5] = splitval[3]

        # Finally grab the infiltration parameters (IL, CL)
        elif col_no == 2:
            splitval = entry.split(',')
            new_row[9] = splitval[0]
            new_row[10] = splitval[1]

        return new_row

    def _loadRowData(row, row_count, row_collection):
        """Loads the data in a specific row of the file.

        Args:
            row(list): containing the row data.
            row_count(int): the current row number.
            required_headers(list): column names that must exist.

        Return:
            rowdatacollection: updated with header row details.
        """
        if '!' in row[-1] or '#' in row[-1]:
            row_collection._addValue('comment', row[-1])
        new_row = [None] * 12

        # Add the row data in the order that it appears in the file
        # from left to right.
        for i in csv_enum.ITERABLE:
            if i < len(row):
                new_row = _disectEntry(i, row[i], new_row)

        for val, item in enumerate(new_row):
            row_collection._addValue(val, item)

    # First entry doesn't want to have a comma in front when formatting.
    row_collection = RowDataCollection()
    types = [1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0]

    # Do the first entry separately because it has a different format string
    row_collection.addToCollection(do.StringData(0, format_str='{0}', default=''))
    for i, t in enumerate(types, 1):
        if t == 0:
            row_collection.addToCollection(do.StringData(i, format_str=', {0}', default=''))
        else:
            row_collection.addToCollection(do.FloatData(i, format_str=', {0}', default='', no_of_dps=3))

    # Add a couple of extra rows to the row_collection for tracking the
    # data in the file.
    row_collection.addToCollection(do.StringData('comment', format_str='{0}', default=''))
    row_collection.addToCollection(do.StringData('actual_header', format_str='{0}', default=''))
    row_collection.addToCollection(do.IntData('row_no', format_str=None, default=''))

    path = datafile.absolutePath()
    try:
        logger.info('Loading data file contents from disc - %s' % (path))
        with open(path, 'rb') as csv_file:
            csv_file = csv.reader(csv_file)

            # Stores the comments found in the file
            comment_lines = []
            first_data_line = False
            line_count = 0

            try:
                # Loop through the contents list loaded from file line-by-line.
                for i, line in enumerate(csv_file, 0):

                    comment = hasCommentOnlyLine(''.join(line), comment_types)
                    if comment or comment == '':
                        comment_lines.append(comment)

                    # If we have a line that isn't a comment or a blank then it is going
                    # to contain materials entries.
                    else:
                        # First non-comment is the headers
                        if first_data_line == False:
                            first_data_line = True
                            _loadHeadData(line, row_collection)
                        else:
                            _loadRowData(line, i, row_collection)

                        row_collection._addValue('row_no', line_count)
                        line_count += 1
                        comment_lines.append(None)
            except IndexError:
                logger.error('This file is not setup/formatted correctly for a Materials.CSV file:\n' + path)
                raise IndexError('File is not correctly formatted for a Materials.csv file')
            except AttributeError:
                logger.error('This file is not setup/formatted correctly for a Materials.CSV file:\n' + path)
                raise AttributeError('File is not correctly formatted for a Materials.csv file')

    except IOError:
        logger.warning('Cannot load file - IOError')
        raise IOError('Cannot load file at: ' + path)

    # Just need to reset the has_changed variable because it will have been
    # set to True while loading everything in.
    for i in range(0, len(csv_enum.ITERABLE)):
        row_collection.getDataObject(i).has_changed = False

    return row_collection, comment_lines, subfile_details


def readMatSubfile(main_datafile, filename, header_list, args_dict):
    """
    """
    value_separator = ','
    comment_types = ['#', '!']
    mat_subfile_enum = dataobj.SubfileMatEnum()
    path = os.path.join(main_datafile.root, filename)
    root = main_datafile.root

    header1 = 'None'
    header2 = 'None'
    if len(header_list) > 0:
        header1 = header_list[0]
        if len(header_list) > 1:
            header2 = header_list[1]

    def _scanfile(filepath):
        """Scans the file before we do any loading to identify the contents.
        Need to do this because the file can be setup in so many way that it
        becomes a headache to work it out in advance. Better to take a little
        bit of extra processing time and do some quick checks first.

        Arguments:
            file_path (str): the path to the subfile.

        Return:
            tuple:
                 list: booleans with whether the column contains
                       data that we want or not.
                 int:  length of the cols list.
                 list: containing all of the first row column data
                 int:  first row with usable data on.
        """
        logger.debug('Scanning Materials file - %s'
                     % (filepath))

        with open(filepath, 'rb') as csv_file:

            csv_file = csv.reader(csv_file)

            cols = []
            head_list = []
            start_row = -1
            for i, row in enumerate(csv_file, 0):
                if "".join(row).strip() == "":
                    break

                for j, col in enumerate(row, 0):
                    if i == 0:
                        cols.append(False)
                        head_list = row
                    elif uuf.isNumeric(col):
                        cols[j] = True
                        if start_row == -1:
                            start_row = i
                    elif cols[j] == True:
                        break

        return cols, len(cols), head_list, start_row

    def _loadHeadData(row, row_collection, col_length):
        """
        """
        new_row = [None] * 12

        comment_indices, length = uuf.findSubstringInList('!', row)
        comment_lines.append(None)

        head1_location = -1
        head2_location = -1
        row_length = len(row)
        for i in range(0, col_length):
            if i < row_length:
                entry = row[i].strip()
                if entry == header1:
                    head1_location = i
                if entry == header2:
                    head2_location = i
                row_collection._addValue('actual_header', entry)

        return row_collection, head1_location, head2_location

    def _loadRowData(row, row_count, row_collection, comment_lines, col_length, start_row):
        """Loads the data in a specific row of the file.

        Args:
            row(list): containing the row data.
            row_count(int): the current row number.
            required_headers(list): column names that must exist.

        Return:
            rowdatacollection: updated with header row details.
        """
        # Any lines that aren't headers, but are above the first row to contain
        # actual data will be stored as comment lines
        if row_count < start_row:
            comment_lines.append(row)
            return row_collection, comment_lines
        else:
            comment_lines.append(None)

        if '!' in row[-1] or '#' in row[-1]:
            row_collection._addValue('comment', row[-1])

        # Add the row data in the order that it appears in the file
        # from left to right.
        for i in range(col_length):
            if i < len(row):
                row_collection._addValue(i, row[i])

        return row_collection, comment_lines

    try:
        logger.info('Loading data file contents from disc - %s' % (path))
        with open(path, 'rb') as csv_file:
            csv_file = csv.reader(csv_file)

            # Do a quick check of the file setup
            cols, col_length, head_list, start_row = _scanfile(path)

            # First entry doesn't want to have a comma in front when formatting.
            # but all of the others do.
            row_collection = RowDataCollection()
            row_collection.addToCollection(do.FloatData(0, format_str=' {0}', default='', no_of_dps=6))
            for i in range(1, len(cols)):
                if cols[i] == True:
                    row_collection.addToCollection(do.FloatData(i, format_str=', {0}', default='', no_of_dps=6))
                else:
                    row_collection.addToCollection(do.StringData(i, format_str=', {0}', default=''))

            row_collection.addToCollection(do.StringData('actual_header', format_str='{0}', default=''), index=0)
            row_collection.addToCollection(do.IntData('row_no', format_str=None, default=''))

            # Stores the comments found in the file
            comment_lines = []
            first_data_line = False
            # Loop through the contents list loaded from file line-by-line.
            for i, line in enumerate(csv_file, 0):

                comment = hasCommentOnlyLine(''.join(line), comment_types)
                if comment or comment == '':
                    comment_lines.append([comment, i])

                # If we have a line that isn't a comment or a blank then it is going
                # to contain materials entries.
                else:
                    # First non-comment is the headers
                    if first_data_line == False:
                        first_data_line = True
                        row_collection, head1_loc, head2_loc = _loadHeadData(line, row_collection, col_length)
                    else:
                        row_collection, comment_lines = _loadRowData(line, i, row_collection, comment_lines, col_length, start_row)

                    row_collection._addValue('row_no', i)

    except IOError:
        logger.warning('Cannot load file - IOError')
        raise IOError('Cannot load file at: ' + path)

    path_holder = filetools.PathHolder(path, root)
    mat_sub = dataobj.DataFileSubfileMat(path_holder, row_collection, comment_lines,
                                         path_holder.filename, head1_loc,
                                         head2_loc)
    return mat_sub


def readTmfFile(datafile):
    """Loads the contents of the Materials CSV file referenced by datafile.

    Loads the data from the file referenced by the given TuflowFile object into
    a :class:'rowdatacollection' and a list of comment only lines.

    Args:
        datafile(TuflowFile): TuflowFile object with file details.

    Return:
        tuple: rowdatacollection, comment_lines(list).

    See Also:
        :class:'rowdatacollection'.
    """
    value_separator = ','
    comment_types = ['#', '!']
    tmf_enum = dataobj.TmfEnum()

    path = datafile.absolutePath()
    value_order = range(11)

    row_collection = RowDataCollection()
    row_collection.addToCollection(do.IntData(0, format_str=None, default=''))
    for i in range(1, 11):
        row_collection.addToCollection(do.FloatData(i, format_str=', {0}', default='', no_of_dps=3))

    # Keep track of any comment lines and the row numbers as well
    row_collection.addToCollection(do.StringData('comment', format_str=' ! {0}', default=''))
    row_collection.addToCollection(do.IntData('row_no', format_str=None, default=''))

    contents = []
    logger.info('Loading data file contents from disc - %s' % (path))
    contents = _loadFileFromDisc(path)

    # Stores the comments found in the file
    comment_lines = []

    # Loop through the contents list loaded from file line-by-line.
    first_data_line = False
    row_count = 0
    for i, line in enumerate(contents, 0):

        comment = hasCommentOnlyLine(line, comment_types)
        if comment or comment == '':
            comment_lines.append(comment)

        # If we have a line that isn't a comment or a blank then it is going
        # to contain materials entries.
        else:
            comment_lines.append(None)
            row_collection = _loadRowData(line, row_count, row_collection, tmf_enum.ITERABLE,
                                          comment_types, value_separator)
            row_count += 1

    # Just need to reset the has_changed variable because it will have been
    # set to True while loading everything in.
    for i in range(0, len(value_order)):
        row_collection.getDataObject(value_order[i]).has_changed = False

    return row_collection, comment_lines


def _loadRowData(line, row_number, row_collection, val_range, comment_types,
                 value_separator):
    """Loads the data in a specific row of the file.

    Args:
        line(string): row as read from file.
        row_number(int): the current row number.
        row_collection(rowdatacollection): object to update.
        val_range(list): Range of values to find in row.
        comment_types(list): characters used for commenting file.
        value_seperator(string): the character used to seperate entries.

    Return:
        rowdatacollection: updated with header row details.
    """
    # If there's a comment put it in the dict
    # Otherwise just set a default value
    line, comment = _extractInlineComment(line, comment_types)

    # Then sort out the other values on the line split by separator value
    split_vals = line.split(value_separator)
    split_length = len(split_vals)
    for i, v in enumerate(val_range):

        # Use the value_order list to know what order the values are in.
        # If we have gone beyond the number of values split we can just put
        # default values in all the other collection data types
        if i < split_length and not split_vals[i].strip() == '':
            row_collection._addValue(i, split_vals[i].strip())
        else:
            row_collection._addValue(i)

    if not comment is None:
        row_collection._addValue('comment', comment)
    row_collection._addValue('row_no', row_number)

    return row_collection


def _loadFileFromDisc(path):
    """Load the file at the given path.

    Args:
        path(string): the absolute path to the file to load.

    Return:
        list containing the contents of the loaded file by line.

    Raises:
        IOError: if the file could not be loaded for some reason.
   """
    contents = []
    try:
        logger.info('Loading file contents from disc')
        contents = filetools.getFile(path)

    except IOError:
        logger.warning('ADataFileComponent cannot load file - IOError')
        raise

    return contents


def hasCommentOnlyLine(line, comment_types):
    """Find if line contains only comments

    Args:
        line(string): line to check for comment only status.
        comment_types(list): the possible comment characters to check for.

    Return:
        String containing line if True or False if not.
    """
    first_char = line.lstrip()[:1]
    if first_char in comment_types or line.strip() == '':
        comment = line.strip()
        return comment
    return False


def _extractInlineComment(line, comment_types):
    """Find if there's a comment on the line and extract it if there is.

    Args:
        line(string): the file line to be checked.
        comment_types(list): containing possible comment characters.

    Return:
        tuple containing the line without the comment parts and the
            rest of the data values on the line (comment, rest-of-line)
   """
    comment = None
    for c in comment_types:
        if c in line:
            split_comment = line.split(c)
            line = split_comment[0]
            comment = split_comment[1]
    return line, comment
