"""
This module contains functions that are intended to be used to analyze
data coming from the CRAAC and SHINY dewars. It is intended to be used
in a pylab environment, so some imports are assumed.
"""

from pylab import *
from HKEBinaryFile import HKEBinaryFile as BinaryFile
from scipy.interpolate import interp1d  # For cal curve interpolation
                                        # functions
                                        # import scipy.interpolate.interp1d


def find_nearest(array,value):
    idx = (abs(array-value)).argmin()
    return array[idx]

def find_nearest_index(array,value):
    idx = (abs(array-value)).argmin()
    return idx

def find_mid_temp(Rs, Ts, midfraction=.5):
    """Find the temperature of the half-max resistance."""
    Rmin, Rmax = min(Rs), max(Rs)
    Rmid = Rmin + (Rmax - Rmin)*midfraction
#    Rmid = (Rmin + Rmax)/2.

    imid = find_nearest_index(Rs, Rmid)
    Tmid = Ts[imid]

    return Tmid

def SHINYload(hkefname, calfname):
    """Load a SHINY data file using the standard recipe."""
    cal = loadtxt(calfname)
    calTs, calRs = cal.T
    RofT = interp1d(calTs, calRs, bounds_error=False, fill_value=-1.)
    calRs = calRs[::-1]
    calTs = calTs[::-1]
    TofR = interp1d(calRs, calTs, bounds_error=False, fill_value=-1.)

    f = BinaryFile(hkefname)

    # Thermometer data
    dataT = f.get_data('SHINY_T4 (5-TRead_Standard): Demod')
    dataT = dataT[..., 0]
    Ts = TofR(dataT)

    # Side 1 resistances
    dataR1 = f.get_data('SHINY_T3 (8-TRead_LR): Demod')
    dataR1 = dataR1.T

    # Side 2 resistances
    dataR2 = f.get_data('SHINY_T1 (4-TRead_LR): Demod')
    dataR2 = dataR2.T

    # Transition temperatures (midpoint method)
    Tcs1 = array([find_mid_temp(rs, Ts) for rs in dataR1])
    Tcs2 = array([find_mid_temp(rs, Ts) for rs in dataR2])

    # Excitation currents
    IsT = f.get_data('SHINY_T4 (5-TRead_Standard): ADac')[0]

    Is1 = f.get_data('SHINY_T3 (8-TRead_LR): ADac')
    Is1 = Is1.T

    Is2 = f.get_data('SHINY_T1 (4-TRead_LR): ADac')
    Is2 = Is2.T

    # Collect data into dictionary
    retdict = {}

    retdict['file'] = f
    #    retdict['dataT'] = dataT
    retdict['Temperatures'] = dataT
    #    retdict['dataR1'] = dataR1
    retdict['Side 1 Resistances'] = dataR1
    #    retdict['dataR2'] = dataR2
    retdict['Side 2 Resistances'] = dataR2
    #    retdict['Tcs1'] = Tcs1
    retdict['Side 1 Transition Temperatures'] = Tcs1
    #    retdict['Tcs2'] = Tcs2
    retdict['Side 2 Transition Temperatures'] = Tcs2
    #    retdict['IsT'] = IsT
    retdict['Thermometer Excitation Current'] = IsT
    #    retdict['Is1'] = Is1
    retdict['Side 1 Excitation Currents'] = Is1
    #    retdict['Is2'] = Is2
    retdict['Side 2 Excitation Currents'] = Is2

    return retdict

def CRAACload(hkefname, calfname):
    """Load a CRAAC data file using the standard recipe."""
    cal = loadtxt(calfname)
    calTs, calRs = cal.T
    RofT = interp1d(calTs, calRs, bounds_error=False, fill_value=-1.)
    calRs = calRs[::-1]
    calTs = calTs[::-1]
    TofR = interp1d(calRs, calTs, bounds_error=False, fill_value=-1.)

    f = BinaryFile(hkefname)

    dataT = f.get_data(0).flatten()
    Ts = TofR(dataT)

    dataR = f.get_data(-6)
    dataR = dataR.T

    Tcs = array([find_mid_temp(rs, Ts) for rs in dataR])

    return Ts, dataR, Tcs, TofR, RofT, f

def comparisonplot(Ts1, Ts2, dataR1, dataR2, Tcs1=None, Tcs2=None, indices=None,
                descriptions=('CRAAC', 'SHINY'), xlim=None, ylim=None,
                xlabel='Temperature (K)', ylabel='Resistance (Ohms)', loc=None, outname=None):
    if indices is None:
        indices = [0, 0]
    elif type(indices) not in (list, ndarray, tuple):
        indices = array([indices, indices])

    if type(descriptions) not in (list, ndarray, tuple):
        descriptions = array([str(descriptions) for i in indices], dtype='str')

    if str(descriptions[0]) is not '':
        descriptions = array([(' - ' + d) for d in descriptions], dtype='str')

    # Grab the default color cycle
    cc = rcParams['axes.color_cycle']

    # Create figure and axes objects
    fig = figure()
    axes = fig.add_subplot('111')
    lines = []

    # Compute Tcs if not provided
    if Tcs1 is None:
        Tcs1 = array([find_mid_temp(rs, Ts1) for rs in dataR1])
    if Tcs2 is None:
        Tcs2 = array([find_mid_temp(rs, Ts2) for rs in dataR2])

    # Plot the lines
    rs1 = dataR1[indices[0]]
    d1 = descriptions[0]
    tc1 = Tcs1[indices[0]]
    c1 = cc[0]
    label1 = 'Ch {i}{d}'.format(i=indices[0], d=d1)
    l1, = axes.plot(Ts1, rs1, c1, label=label1)
    lines.append(l1)
    axvline(tc1, color=c1, ls='--')

    rs2 = dataR2[indices[1]]
    d2 = descriptions[1]
    tc2 = Tcs2[indices[1]]
    c2 = cc[1]
    label2 = 'Ch {i}{d}'.format(i=indices[1], d=d2)
    l2, = axes.plot(Ts2, rs2, c2, label=label2)
    lines.append(l2)
    axvline(tc2, color=c2, ls='--')

    if xlim is None:
        tcs = (Tcs1[indices[0]], Tcs2[indices[1]])
        tcmin, tcmax = min(tcs), max(tcs)
        delta = max(tcmax - tcmin, .1)
        xlim = array([tcmin - delta, tcmax + delta])

    axes.set_xlabel(str(xlabel))
    axes.set_ylabel(str(ylabel))
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)

    axes.legend(loc=loc)

    if outname is not None:
        savefig(outname, dpi=300)

    return fig, axes, lines

def groupplot(Ts, dataR, Tcs=None, indices=None, descriptions=None, xlim=None, ylim=None,
                xlabel='Temperature (K)', ylabel='Resistance (Ohms)', loc=None, outname=None):
    if indices is None:
        indices = [0]
    elif type(indices) not in (list, ndarray):
        indices = array([indices])

    if descriptions is None:
        descriptions = empty_like(indices, dtype='str')
    elif type(descriptions) not in (list, ndarray):
        descriptions = array([str(descriptions) for i in indices], dtype='str')

    if str(descriptions[0]) is not '':
        descriptions = array([(' - ' + d) for d in descriptions], dtype='str')

    # Grab the default color cycle
    cc = rcParams['axes.color_cycle']

    # Create figure and axes objects
    fig = figure()
    axes = fig.add_subplot('111')
    lines = []

    # Compute Tcs if not provided
    if Tcs is None:
        Tcs = array([find_mid_temp(rs, Ts) for rs in dataR])

    # Plot the lines
    for i, index in enumerate(indices):
        rs = dataR[index]
        d = descriptions[i]
        tc = Tcs[index]
        c = cc[i]
        label = 'Ch {i}{d}'.format(i=index, d=d)
        l, = axes.plot(Ts, dataR[index], c, label=label)
        lines.append(l)

        # Need to manually specify color so it matches plot line
        axvline(tc, color=c, ls='--')   # Add T_c marker line

    if xlim is None:
        tcs = array([Tcs[i] for i in indices])
        tcmin, tcmax = min(tcs), max(tcs)
        delta = max(tcmax - tcmin, .1)
        xlim = array([tcmin - delta, tcmax + delta])

    axes.set_xlabel(str(xlabel))
    axes.set_ylabel(str(ylabel))
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)

    # Measure the noise level of the channels
    sys = []
    Tmin = min(Ts)
    for i in indices:
        rs = dataR[i]
        tc = Tcs[i]
        Tcutoff = (Tmin + tc)/2.
        noiseRs = rs[Ts < Tcutoff]
        sy = std(noiseRs)
        sys.append(sy)

    ynoise = max(sys)
    ynoise = 10**(floor(log10(ynoise)))

    axes.set_yscale('symlog', linthreshy=ynoise)
    axes.legend(loc=loc)

    if outname is not None:
        savefig(outname, dpi=300)

    return fig, axes, lines
