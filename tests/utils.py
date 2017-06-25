import os

def fakeAbsPath(path):
    '''
    Make a pretend filepath 'absolute' for the current os.
    Will massage absolute paths for the wrong OS to abs paths
    for current os
    '''
    if os.path.isabs(path):
        # It is already an absolut path
        newpath = path
    elif os.name == 'posix':
        # We may have been given a windows path, so remove the drive and
        # make it root dir
        newpath = path.replace('c:', '').replace('\\', os.sep)
        if not newpath.startswith('/'):
            newpath = '/{}'.format(newpath)
    else:
        newpath = 'c:{}{}'.format(os.sep, path)

    return newpath
