.. _pathholder-top:

**********
PathHolder
**********

The PathHolder class is a general purpose class used in most parts of the SHIP
library for storing, accessing and updating file path data. Both Ief and
DatCollection have an instance of PathHolder (called path_holder) that they use
to store the details of their filepath. The TuflowFile class (and subclasses)
inherit from PathHolder directly to manage their path variables.

########
Overview
########

The PathHolder class can be found in the ship.utils.filetools.py module. It
only holds a few variables:

   - **root(str)**: this can be everything from the 'C:/' (on windows) through to the
     folder above the file name, or it could be to a differnt folder with a 
     relative_root supplied (see below).
   - **relative_root(str)**: a section of path relative to another folder (e.g.
     '..\..\myfolder'). This is useful when you have a main root folder and
     all other files should be relative to it.
   - **filename(str)**: the name of the file. Includes everything after the final
     folder and before the extension.
   - **extension(str)**: the file extension. 
   - **path_as_read(str)**: this is never changed after the PathHolder is made. It
     stores the path given to the constructor, unchanged.

PathHolder also provides a number of interfaces for providing common filepath
manipulations. These include:

   - **absolutePath()**: returns the absolute path.
   - **relativePath()**: returns the relative path.
   - **filenameAndExtension()**: return the filename + extension.
   - **exists()**: returns True if the path exists ro False otherwise.
   - **dir()**: returns the directory component of the path.
   - **finalFolder()**: returns the last folder in the path (i.e. the folder 
     immediately before the filename.
   - **setFinalFolder(str)**: updates the final folder.
