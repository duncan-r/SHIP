"""

 Summary:
     Contains a selection of file dialogs and useful implementations of Qt
     classes that are likely to be used by many applications.
 
    Contains file dialogues for use in accessing files for opening, saving,
    etc. These must be kept in a seperate module for a couple of reasons.
    - They use PyQt4 and we might want to update to PyQt5 or use a different
      interface for the GUI builds.
    - If PyQt4 is not installed on the user machine this will stop the whole
      library from working if we keep it in the FileTools.py module.

    The FileTools.py module will try and load this one. If it fails then it
    sets a variable that the methods in FileTools.py will check and know not
    to try and access any of the GUI related code.
    
    In most cases it is not necessary to create an instance of the MyFileDialogs
    class. Instead the functions in the filetools.py module should be used to
    retrieve the different file paths.
    
    All QString's are converted to python str objects before returning.

 Author:  
     Duncan Runnacles.

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


try:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
    HAS_QT = True

except Exception:
    logger.warning('Unable to load Qt modules - cannot launch file dialogues')
    HAS_QT = False


class MyFileDialogs(QtGui.QFileDialog):
    """Class for launching file dialogs.

    If the Qt modules could not be loaded  when the module was imported all of
    functions in this class will return False because it isn't possible to
    launch the dialogs.

    Note:
        Perhaps this should be a Singleton? So that we don't have  hundreds
        of these classes all over the place taking up space. I think that I
        might make the Gui application use QThreads to lauch plugins etc so
        need to consider that when messing around in here.
    """

    def openFileDialog(self, path='', file_types='ALL (*.*)', multi_file=False):
        """ Launches an open-file dialog.

        file_types should be a formatted string setup as follows:
        "CSV (*.csv);;TXT (*.txt)"

        Args:
            path (str): the preset path to launch the dialog in.
            file_types (str): the extensions to filter the files with. 

        Returns:
            str - containing the chosen file path or False if cancelled.
        """
        if not HAS_QT:
            return False

        if not multi_file:
            filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Open File', path, file_types))
            if not filename == '':
                logger.info('Opening file: ' + filename)
                return filename
            else:
                logger.info('User cancelled file open process')
                return False
        else:
            filenames = QtGui.QFileDialog.getOpenFileNames(self, 'Open Files', path, file_types)
            if not len(filenames) < 1:
                str_names = []
                for f in filenames:
                    str_names.append(str(f))
                logger.info('Opening files: %s' % str(str_names))
                return str_names
            else:
                logger.info('User cancelled file open process')
                return False

    def saveFileDialog(self, path='', file_types='ALL (*.*)'):
        """Launches an save-file dialog

        file_types should be a formatted string setup as follows:
        "CSV (*.csv);;TXT (*.txt)"

        Args:
            path (str): the preset path to launch the dialog in.
            file_types (str): the extensions to filter the files with  

        Returns:
            str - containing the chosen file path or False if cancelled.
        """
        filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save File', path, file_types))
        if not filename == '':
            logger.info('Saving file: Filename = ' + filename)
            return filename
        else:
            logger.info('User cancelled file save process')
            return False

    def dirFileDialog(self, path=''):
        """Launches a dialog to choose directories from.

        Args:
            path (str): Optional - the preset path to launch the dialog in.

        Returns:
            str - containing the chosen file path or False if cancelled.
        """
        file_path = str(QtGui.QFileDialog.getExistingDirectory(self,
                                                               caption='Select Directory', directory=path,
                                                               options=QtGui.QFileDialog.ShowDirsOnly))

        if not file_path == '':
            logger.info('Selected directory: Filepath = ' + file_path)
            return file_path
        else:
            logger.info('User cancelled get directory process')
            return False


class QNumericSortTableWidgetItem (QtGui.QTableWidgetItem):
    """Custom implementation of the QTableWidgetItem class.

    Allows sorting of numerical values by overridding the default __lt__
    operator to do a numerical comparision.
    """

    def __init__(self, value):
        super(QNumericSortTableWidgetItem, self).__init__(QtCore.QString('%s' % value))

    def __lt__(self, other):
        """Check order of two values.

        Tries to convert the value to a float. If successful it will return 
        the order of those two values. 

        If value is not numeric or is not a QCustomTableWidgetItem type it
        will return the standard string compare output.

        Args:
            other(QTableWidgetItem): value to compare with that stored by this.

        Return:
            Bool - True if given value is less than this.
        """
        if (isinstance(other, QNumericSortTableWidgetItem)):
            try:
                self_data_value = float(self.data(QtCore.Qt.EditRole).toString())
                other_data_value = float(other.data(QtCore.Qt.EditRole).toString())
            except:
                return QtGui.QTableWidgetItem.__lt__(self, other)
            return self_data_value < other_data_value
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)
