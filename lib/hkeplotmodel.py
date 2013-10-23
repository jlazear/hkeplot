"""
This HKEModel class is meant to retrieve and store sets of
HKEBinaryFile data.

Example usage:

>>> hkem = HKEModel()
>>> hkem.loadfile('hke_20130201_001.dat', 'U02728.txt')
>>> hkem.keys()
[u'hke_20130207_009.dat']
>>> hkem['hke_20130201_001.dat'] # Dictionary of data
"""

from HKEBinaryFile import HKEBinaryFile as BinaryFile
from HKEBinaryFile import HKEInvalidRegisterError
from hkeconfig import HKEConfig
from parseboards import parse_boards_file, construct_register_name, \
                        save_board_file
from scipy.interpolate import interp1d
from numpy import *
import os
from tempfile import TemporaryFile
from collections import Iterable
from types import StringTypes


class HKEModel(object):
    """
    A class for storing and working with loaded HKEBinaryFile files.

    Once made, this class should behave essentially like a dictionary
    of data files, i.e. one could do:

    >>> hkem = HKEModel()
    >>> hkem.loadfile('hke_20130201_001.dat', 'U02728.txt')
    >>> hkem.keys()
    [u'hke_20130207_009.dat']
    >>> hkem['hke_20130201_001.dat'] # Dictionary of data

    But the class has the added benefit that we can include methods
    for loading the data in an intelligent way,
    i.e. HKEModel.loadfile().

    A caveat here is that HKEModel does not support assignment, so
    something like

    >>> hkem['hke_20130201_002.dat'] = dict{...}

    will not work.
    """
    def __init__(self, datafiles=None, calfiles=None, boardscfgfiles=None,
                 taddresses=None, tchannels=None):
        self.datafiles = {}
        self.orderedkeys = []

        if datafiles is None:
            return

        if not isinstance(datafiles, StringTypes):
            datafiles = [datafiles]
        if calfiles is None:
            print "No calibration file selected. No files loaded."
            return
        if not isinstance(boardscfgfiles, Iterable) or \
            isinstance(boardscfgfiles, StringTypes):
            boardscfgfiles = [boardscfgfiles for i in datafiles]
        if not isinstance(taddresses, Iterable):
            taddresses = [taddresses for i in datafiles]
        if not isinstance(tchannels, Iterable):
            tchannels = [tchannels for i in datafiles]

        for i, f in enumerate(datafiles):
            try:
                name = os.path.basename(f)
                bcfgf = boardscfgfiles[i]
                calf = calfiles[i]
                taddress = taddresses[i]
                tchannel = tchannels[i]
                toadd = self.loadfile(f, calf, bcfgf, taddress, tchannel)
                self.datafiles[name] = toadd
            except Exception as ex:
                print ex
                raise ex

    def loadfile(self, hkefname, calfname, taddress=None, tchannel=None,
                 bcfgfile=None, description=None, handleerrors=True):
        hkefname = os.path.abspath(hkefname)
        folder, name = os.path.split(hkefname)
        fn, ext = os.path.splitext(hkefname)
        newcfgname = fn + '_boards.txt'

        calfname = os.path.abspath(calfname)

        hkefile = BinaryFile(hkefname)
        if bcfgfile is None:
            bcfgfile = newcfgname
        try:
            boardsdict = parse_boards_file(bcfgfile)
        except IOError:
            raise HKEPlotLoadError(hkefname, calfname)

        boards = boardsdict['boards']

        # Load thermometer interpolation curves
        cal = self._cal_load(calfname)
        calTs, calRs = cal.T
        RofT = interp1d(calTs, calRs, bounds_error=False,
                        fill_value=-1.)
        calRs = calRs[::-1]
        calTs = calTs[::-1]
        TofR = interp1d(calRs, calTs, bounds_error=False,
                        fill_value=-1.)

        # Load data from datafile
        for addr in boards.keys():
            t = boards[addr]['type']
            if t not in ['pmaster']:
                regname = construct_register_name(boards, addr)
                boards[addr]['register_name'] = regname
                data = hkefile.get_data(regname).T
                boards[addr]['data'] = data

        # Use first available data register as T, if none specified.
        if taddress is None:
            treg = boards.values()[0]
            taddress = treg['address']
            tchannel = 0
        else:
            treg = boards[taddress]
        dataT = treg['data'][tchannel]

        Ts = TofR(dataT)

        # Compute TCs
        for addr in boards.keys():
            t = boards[addr]['type']
            if t not in ['pmaster']:
                data = boards[addr]['data']
                Tcs = array([self.find_mid_temp(rs, Ts) for rs in data])
                boards[addr]['Tcs'] = Tcs

        boardsdict['filename'] = os.path.abspath(hkefname)
        boardsdict['file'] = hkefile
        boardsdict['calfile'] = calfname
        boardsdict['boardsfile'] = newcfgname
        if isinstance(description, StringTypes):
            boardsdict['description'] = description

        boardsdict['temperature'] = {'address': taddress,
                                     'channel': tchannel,
                                     'Ts': Ts}

        # Save copy of the config file.
        if not os.path.isfile(newcfgname):
            save_board_file(boardsdict, newcfgname)

        self.datafiles[name] = boardsdict
        self.orderedkeys.append(name)

        return True

    ########################################
    ########## Utility Functions ###########
    ########################################

    def _cal_load(self, calfname):
        """
        Load a cal curve. This method is more robust against format
        inconsistencies in the cal file, at the cost of a small amount
        of memory.
        """
        try:
            cal = loadtxt(calfname)
            return cal
        except ValueError:
            tmp = TemporaryFile(mode='w+')
            with open(calfname) as f:
                for line in f:
                    if 'UNITS' in line:
                        line = '# ' + line
                    tmp.write(line)
            tmp.seek(0)
            cal = loadtxt(tmp)
            return cal

    def find_nearest(self, array, value):
        idx = (abs(array-value)).argmin()
        return array[idx]

    def find_nearest_index(self, array, value):
        idx = (abs(array-value)).argmin()
        return idx

    def find_mid_temp(self, Rs, Ts, midfraction=.5):
        """Find the temperature of the half-max resistance."""
        Rmin, Rmax = min(Rs), max(Rs)
        Rmid = Rmin + (Rmax - Rmin)*midfraction
        #    Rmid = (Rmin + Rmax)/2.

        imid = self.find_nearest_index(Rs, Rmid)
        Tmid = Ts[imid]

        return Tmid

    def rename(self, name, newname):
        """
        Renames a model item. The filename from which the model item
        is derived is still contained in model['name']['filename'].
        """
        if isinstance(name, int):
            num = name + 0
            name = self.keys()[name]
        else:
            num = self.orderedkeys.index(name)
        self.datafiles[newname] = self.datafiles.pop(name)
        self.orderedkeys[num] = newname

    def change_sources(self, name, treg, tch, s1reg, s2reg=None):
        model = self[name]
        f = model['file']
        hkefname = f.filename
        calfname = model['calfile']
        desc = model['description']
        dewar = model['dewar']

        self.__delitem__(name)

        self.loadfile(hkefname, calfname, description=desc,
                      dewar=dewar, tregister=treg, tchannel=tch,
                      r1register=s1reg, r2register=s2reg)
        self.rename(-1, name)

    def add_descriptions(self, name, descriptions, side=1):
        """
        Add descriptions to the channels.
        """
        datafile = self.datafiles[name]
        chstr = "Side {s} Resistances".format(s=side)
        toaddstr = "Side {s} Descriptions".format(s=side)
        length = len(datafile[chstr])
        if not isinstance(descriptions, (list, tuple, ndarray)):
            descriptions = [descriptions for i in range(length)]
        else:
            descriptions = list(descriptions)
            desclength = len(descriptions)
            difflen = length - desclength
            difflist = ['' for i in range(difflen)]
            descriptions.extend(difflist)
        datafile[toaddstr] = descriptions

    ########################################
    ########## Special Functions ###########
    ########################################

    # We are overwriting the getitem/setitem (i.e. object[key]
    # functionality) so that the base object can behave as a container
    # without having to go through the extra layer of calling
    # HKEModel.datafiles.
    def __getitem__(self, key):
        return self.datafiles[key]

    def __delitem__(self, key):
        self.orderedkeys.remove(key)
        return self.datafiles.__delitem__(key)

    def __setitem__(self, *args):
        print "The HKEModel class does not support item assignment."

    def keys(self):
        return self.orderedkeys

    def __repr__(self):
        keys = self.orderedkeys
        if not keys:
            keys = 'None'
        else:
            keys = str(keys)
        tp = '<HKEModel object containing the data files: \
{}>'.format(keys)
        return tp


class HKEPlotError(Exception):
    """
    Generic error for hkeplot.
    """
    pass


class HKEPlotLoadError(HKEPlotError):
    """
    An error indicating an error with loading a file.
    """
    def __init__(self, fname, calfname):
        self.msg = ("Failed to load data.\n\n" +
                    "Data file: {0}\n\n".format(fname) +
                    "Cal file: {0}".format(calfname))

    def __str__(self):
        return self.msg
