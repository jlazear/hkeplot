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
from scipy.interpolate import interp1d
from numpy import *
import os
from tempfile import TemporaryFile


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
    def __init__(self, datafiles=None, calfiles=None, dewars=None):
        self.datafiles = {}
        self.orderedkeys = []

        if datafiles is not None:
            if type(datafiles) not in (list, tuple, ndarray):
                datafiles = [datafiles]
            if calfiles is None:
                print "No calibration file selected. No files loaded."
                return
            if type(dewars) not in (list, tuple, ndarray):
                dewars = [dewars for i in datafiles]
            elif type(calfiles) not in (list, tuple, ndarray):
                calfiles = [calfiles for i in datafiles]
            for i, f in enumerate(datafiles):
                try:
                    name = os.path.basename(f)
                    calf = calfiles[i]
                    toadd = self.loadfile(f, calf)
                    self.datafiles[name] = toadd
                except Exception as ex:
                    print ex
                    raise ex

    def loadfile(self, hkefname, calfname,
                 description='No description', dewar='SHINY',
                 handleerrors=True, tregister=None, tchannel=None,
                 r1register=None, r2register=None):
        dewar = dewar.lower()
        try:
            name = os.path.basename(hkefname)
            hkefile = BinaryFile(hkefname)
            if dewar in 'shiny':
                toadd = self._SHINYload(hkefile, calfname,
                                        tregister=tregister,
                                        tchannel=tchannel,
                                        r1register=r1register,
                                        r2register=r2register)
            elif dewar in 'craac':
                toadd = self._CRAACload(hkefile, calfname,
                                        tregister=tregister,
                                        tchannel=tchannel,
                                        r1register=r1register,
                                        r2register=r2register)
            print "Successfully loaded file: {fname}".format(
                fname=hkefname)
        except IOError:
            print "The file {fn} does not exist.".format(fn=hkefname)
            if not handleerrors:
                raise HKEPlotLoadError(hkefname, calfname)
            return
        except (KeyError, HKEInvalidRegisterError, IndexError):
            # If the SHINY load fails, try the CRAAC load.
            print "SHINY load failed... Trying CRAAC load."
            name = os.path.basename(hkefname)
            toadd = self._CRAACload(hkefile, calfname)
            toadd['dewar'] = 'craac'
            print "Successfully loaded file: {fname}".format(
                fname=hkefname)
        # except Exception as ex:
        #     print ex
        #     raise ex

        toadd['filename'] = name
        toadd['description'] = str(description)

        self.datafiles[name] = toadd
        self.orderedkeys.append(name)

        if toadd['dewar'] is 'shiny':
            self.add_descriptions(name, '', side=1)
            self.add_descriptions(name, '', side=2)
        elif toadd['dewar'] is 'craac':
            self.add_descriptions(name, '', side=1)

        return True

    def _SHINYload(self, hkefile, calfname, tregister=None,
                   tchannel=None, r1register=None, r2register=None):
        """Load a SHINY data file using the standard recipe."""
        registers = hkefile.list_registers()
        if tregister is None:
            # tregister = registers[57]
            # tregister = 'SHINY_T4 (5-TRead_Standard): Demod'
            tregister = 'RuOx Thermometers (5-TRead_Standard): Demod'
        if tchannel is None:
            tchannel = 0
        if r1register is None:
            # r1register = registers[69]
            # r1register = 'SHINY_T3 (8-TRead_LR): Demod'
            # r1register = 'Sierra PCB Resistivity #2 (8-TRead_LR): Demod'
            r1register = 'PIPER Detector Samples 1-7 (7-TRead_LR): Demod'
        if r2register is None:
            # r2register = registers[53]
            # r2register = 'SHINY_T1 (4-TRead_LR): Demod'
            # r2register = 'Sierra PCB Resistivity #2 (7-TRead_LR): Demod'
            # r2register = 'RuOx Thermometers (7-TRead_Standard): Demod'
            r2register = 'PIPER Detector Samples 8-13 (8-TRead_LR): Demod'

        cal = self._cal_load(calfname)
        calTs, calRs = cal.T
        RofT = interp1d(calTs, calRs, bounds_error=False,
                        fill_value=-1.)
        calRs = calRs[::-1]
        calTs = calTs[::-1]
        TofR = interp1d(calRs, calTs, bounds_error=False,
                        fill_value=-1.)

        # Thermometer data
        dataT = hkefile.get_data(tregister)
        if 'DSPID' in tregister:
            dataT = dataT.flatten()
        else:
            dataT = dataT[..., tchannel]
        Ts = TofR(dataT)

        # Side 1 resistances
        dataR1 = hkefile.get_data(r1register)
        dataR1 = dataR1.T

        # Side 2 resistances
        dataR2 = hkefile.get_data(r2register)
        dataR2 = dataR2.T

        # Transition temperatures (midpoint method)
        Tcs1 = array([self.find_mid_temp(rs, Ts) for rs in dataR1])
        Tcs2 = array([self.find_mid_temp(rs, Ts) for rs in dataR2])

        # Excitation currents
        IsT = hkefile.get_data(tregister[:-5] + 'ADac')[0]

        Is1 = hkefile.get_data(r1register[:-5] + 'ADac')
        Is1 = Is1.T

        Is2 = hkefile.get_data(r2register[:-5] + 'ADac')
        Is2 = Is2.T

        # Collect data into dictionary
        retdict = {}

        retdict['file'] = hkefile
        retdict['calfile'] = calfname
        retdict['Temperatures'] = Ts
        retdict['Side 1 Resistances'] = dataR1
        retdict['Side 2 Resistances'] = dataR2
        retdict['Side 1 Transition Temperatures'] = Tcs1
        retdict['Side 2 Transition Temperatures'] = Tcs2
        retdict['Thermometer Excitation Current'] = IsT
        retdict['Side 1 Excitation Currents'] = Is1
        retdict['Side 2 Excitation Currents'] = Is2
        retdict['Temperature Register'] = tregister
        retdict['Temperature Channel'] = tchannel
        retdict['Side 1 Register'] = r1register
        retdict['Side 2 Register'] = r2register
        retdict['dewar'] = 'shiny'

        return retdict

    def _CRAACload(self, hkefile, calfname, tregister=None,
                   tchannel=0, r1register=None, r2register=None):
        """Load a CRAAC data file using the standard recipe."""
        if tregister is None:
            tregister = 'ADR Root coil (1-DSPID): Demod'
        if tchannel is None:
            tchannel = 0
        if r1register is None:
            r1register = '4W Quadrant (4-TRead_LR): Demod'

        # cal = loadtxt(calfname)
        cal = self._cal_load(calfname)
        calTs, calRs = cal.T
        RofT = interp1d(calTs, calRs, bounds_error=False,
                        fill_value=-1.)
        calRs = calRs[::-1]
        calTs = calTs[::-1]
        TofR = interp1d(calRs, calTs, bounds_error=False,
                        fill_value=-1.)

        # Thermometer Data
        if 'DSPID' in tregister:
            dataT = hkefile.get_data(tregister).flatten()
        else:
            dataT = dataT[..., tchannel]
        Ts = TofR(dataT)

        # Side 1 resistances
        dataR1 = hkefile.get_data(r1register)
        dataR1 = dataR1.T

        # Transition temperatures (midpoint method)
        Tcs1 = array([self.find_mid_temp(rs, Ts) for rs in dataR1])

        # Excitation currents
        IsT = hkefile.get_data('ADR Root coil (1-DSPID): ADac')[0]

        Is1 = hkefile.get_data('4W Quadrant (4-TRead_LR): ADac')
        Is1 = Is1.T

        # Collect data into dictionary
        retdict = {}

        retdict['file'] = hkefile
        retdict['calfile'] = calfname
        retdict['Temperatures'] = Ts
        retdict['Side 1 Resistances'] = dataR1
        retdict['Side 1 Transition Temperatures'] = Tcs1
        retdict['Thermometer Excitation Current'] = IsT
        retdict['Side 1 Excitation Currents'] = Is1
        retdict['Temperature Register'] = tregister
        retdict['Temperature Channel'] = tchannel
        retdict['Side 1 Register'] = r1register
        retdict['dewar'] = 'craac'

        return retdict

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
