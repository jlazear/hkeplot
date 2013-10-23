"""
The HKEPlotter class is meant to create and serve up figures and plots
of the data contained in an HKEModel model object.
"""

# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Subplot, Axes
import matplotlib as mpl


class HKEPlotter(object):
    """
    A class for creating and serving up the figure objects associated
    with plots from HKE data.

    Example usage:
    >>> model = HKEModel()
    >>> model.loadfile('hke_20130201_001.dat', 'U02728.txt')
    >>> plotter = HKEPlotter(model)
    >>>
    """
    def __init__(self, model=None):
        self.model = model
        self.figure = None
        self.axes = None
        self.lines = []
        self.axvlines = []
        self.axhlines = []
        self.cc = mpl.rcParams['axes.color_cycle']
        self.usedcc = []

    def makefigure(self, figsize=(4., 4.), dpi=100, **kwargs):
        self.figure = Figure(figsize=figsize, dpi=dpi, **kwargs)
        return self.figure

    def add_subplot(self, *args, **kwargs):
        if type(self.figure) is not Figure:
            print "Figure not yet initialized. Make the figure first."
            return

        self.axes = self.figure.add_subplot(*args, **kwargs)
        return self.axes

    def getnextcolor(self):
        """
        Gets the next unused color in the colormap.
        """
        self.usedcc = [line.get_c() for line in self.axes.lines]
        for c in self.cc:
            if c not in self.usedcc:
                return c

        # Only gets here if all colors already used...
        i = len(self.axes.lines)
        numc = len(self.cc)
        i = i % numc
        return self.cc[i]

    def plot(self, *args, **kwargs):
        color = self.getnextcolor()
        newline, = self.axes.plot(*args, color=color, **kwargs)

        linewidth = newline.get_linewidth()

        newlinedict = {'line': newline, 'color': color, 'vlines': [],
                       'hlines': [], 'linewidth': linewidth,
                       'highlighted': False, 'highlight factor': 1.0}
        self.lines.append(newlinedict)

        return newline

    def resetplot(self):
        self.clearplot()
        self.axes.clear()

    def clearplot(self):
        self._killlines()
        self.lines = []

    def _killlines(self):
        for ld in self.lines:
            line = ld['line']
            self.axes.lines.remove(line)
        self.usedcc = []

    def _checkfigure(self):
        """
        Checks to see if the figure has been initialized
        sufficiently. Raises a HKEPlotterNotInitializedError if this
        check fails.
        """
        if ((type(self.figure) is Figure) and
            (type(self.axes) in (Subplot, Axes))):
            return
        else:
            raise HKEPlotterNotInitializedError(self.figure,
                                                self.axes)

    # def RvsTPlot(self, datafile, dataRname, index, description='',
    #              Tcline=True):
    def RvsTPlot(self, datafile, boardindex, chindex, description='',
                 Tcline=True):
        """
        Makes an R vs T plot from a specified datafile.
        """
        try:
            self._checkfigure()
        except HKEPlotterNotInitializedError(self.figure,
                                             self.axes) as e:
            print e

        temperature = datafile['temperature']
        Ts = temperature['Ts']

        board = datafile['boards'][boardindex]
        register = board['registers'][chindex]

        dataR = board['data']
        Rs = dataR[chindex]

        chdesc = register['name']
        print "description = ", repr(description) #DELME
        if description:
            description = ' - ' + description
        print "chdesc = ", repr(chdesc) #DELME
        if chdesc:
            description = description + ' - ' + chdesc

        label = 'Ch {i}{d}'.format(i=chindex, d=description)
        line = self.plot(Ts, Rs, label=label)

        linedict = self._get_linedict(line)
        linedict['label'] = label

        Tc = board['Tcs'][chindex]
        linedict['Tc'] = Tc

        if Tcline:
            self.addTcline(line, Tc)

        return linedict

        # Ts = datafile['Temperatures']
        # dataR = datafile[dataRname]
        # Rs = dataR[index]

        # sidenum = dataRname.split()[1]
        # desclist = datafile['Side {s} Descriptions'.format(s=sidenum)]
        # chdesc = desclist[index]

        # if description:
        #     description = ' - ' + description
        # if chdesc:
        #     description = description + ' - ' + chdesc

        # label = 'Ch {i}{d}'.format(i=index, d=description)
        # line = self.plot(Ts, Rs, label=label)

        # linedict = self._get_linedict(line)
        # linedict['label'] = label

        # Tcs = datafile['Side {i} Transition Temperatures'.format(i=sidenum)]
        # Tc = Tcs[index]
        # linedict['Tc'] = Tc

        # if Tcline:
        #     self.addTcline(line, Tc)

        # return linedict

    def _get_linedict(self, line):
        """
        Finds and returns the line dictionary in self.lines that
        contains the specified line.
        """
        if (isinstance(line, dict) and
            (line in self.lines)):
            return line
        for linedict in self.lines:
            if line in linedict.itervalues():
                ld = linedict
        try:
            return ld
        except NameError:
            raise HKEPlotterLineDoesNotExistError(line)

    def addTcline(self, line, temperature=None):
        """
        Add a vertical line corresponding to line at the specified
        temperature.
        """
        self._checkfigure()
        ld = self._get_linedict(line)
        line = ld['line']
        if temperature is None:
            temperature = ld['Tc']
        color = line.get_c()
        axvl = self.axes.axvline(temperature, color=color, ls='--')
        # self.axvlines.append(axvl)
        ld['vlines'].append(axvl)

    def delTcline(self, line):
        """
        Remove a vertical line corresponding to line.
        """
        self._checkfigure()
        ld = self._get_linedict(line)
        for vline in ld['vlines']:
            vline.remove()
        ld['vlines'] = []

    def highlight_line(self, line, factor=1.5):
        """
        Highlight a line by making its linewidth slightly larger.
        """
        self._checkfigure()
        ld = self._get_linedict(line)
        ld['highlighted'] = True
        ld['highlight factor'] = factor
        self.update_lines()

    def unhighlight_line(self, line):
        """
        Remove the highlighting of a line by restoring its linewidth
        to the original size.
        """
        self._checkfigure()
        ld = self._get_linedict(line)
        ld['highlighted'] = False
        self.update_lines()

    def delete_line(self, line):
        """
        Remove a line and all lines related to it from the figure.
        """
        self._checkfigure()
        ld = self._get_linedict(line)
        self.delTcline(ld)
        line = ld['line']
        line.remove()
        self.lines.remove(ld)

    def update_lines(self):
        """
        Update all of the properties of the lines to match those
        specified by the lines dictionaries.
        """
        self._checkfigure()
        for ld in self.lines:
            line = ld['line']

            color = ld['color']
            line.set_color(color)

            lw = ld['linewidth']
            hlf = ld['highlight factor']
            highlight = hlf if ld['highlighted'] else 1.0
            lw = lw*highlight
            line.set_linewidth(lw)

            for vline in ld['vlines']:
                vline.set_color(color)
                vline.set_linestyle('--')
                vline.set_linewidth(lw)

            for hline in ld['vlines']:
                hline.set_color(color)
                hline.set_linestyle('--')
                hline.set_linewidth(lw)

    def xscale(self, newscale, linthreshx=1.e-4):
        """
        Change the scale of the x axis.
        """
        self._checkfigure()
        if newscale == 'symlog':
            self.axes.set_xscale(newscale, linthreshx=linthreshx)
        else:
            self.axes.set_xscale(newscale)

    def yscale(self, newscale, linthreshy=1.e-4):
        """
        Change the scale of the y axis.
        """
        self._checkfigure()
        if newscale == 'symlog':
            self.axes.set_yscale(newscale, linthreshy=linthreshy)
        else:
            self.axes.set_yscale(newscale)

    def autorange(self):
        """
        Automatically adjusts the range of the x and y axes to fit the
        data.
        """
        self._checkfigure()
        self.axes.autoscale_view(True)

    def legend(self, loc=None):
        """
        Create a legend.
        """
        self._checkfigure()
        self.axes.legend(loc=loc)

    def hide_legend(self):
        """
        Hide the legend.
        """
        self._checkfigure()
        leg = self.axes.get_legend()
        if leg:
            leg.set_visible(False)

    def title(self, title):
        """
        Set the title.
        """
        self._checkfigure()
        self.axes.set_title(title)

    def xlabel(self, xlabel):
        """
        Set the x label.
        """
        self._checkfigure()
        self.axes.set_xlabel(xlabel)

    def ylabel(self, ylabel):
        """
        Set the y label.
        """
        self._checkfigure()
        self.axes.set_ylabel(ylabel)

    def savefig(self, filename, dpi=300):
        """
        Save a figure to disk with the specified filename.
        """
        self._checkfigure()
        self.figure.savefig(filename, dpi=dpi)

    def draw(self):
        """
        Show and redraw the figure. Generally not useful if HKEPlotter
        is being used to serve up figures to a different front-end,
        but is useful for interactive use of HKEPlotter on its own.
        """
        self.figure.show()
        self.figure.canvas.draw()


class HKEPlotterError(Exception):
    """
    A base class for HKEPlotter exceptions.
    """
    pass


class HKEPlotterNotInitializedError(HKEPlotterError):
    """
    An error indicating that the HKEPlotter object has not been
    initialized.
    """
    def __init__(self, fig, axes):
        self.fig = fig
        self.axes = axes

        figflag = False
        axesflag = False

        if type(self.fig) is not Figure:
            figflag = True
        if type(self.axes) not in (Subplot, Axes):
            axesflag = True

        if figflag and axesflag:
            toadd = " figure and axes"
        elif figflag:
            toadd = " figure"
        else:
            toadd = " axes"

        self.msg = 'The following HKEPlotter parts have not been \
initialized: {toadd}'.format(toadd=toadd)

    def __str__(self):
        return self.msg


class HKEPlotterLineDoesNotExistError(HKEPlotterError):
    """
    An error indicating that the HKEPlotter does not recognize the
    specified line as one that it owns.
    """
    def __init__(self, line):
        self.line = line
        self.msg = 'The HKEPlotter instance does not recognize the \
specified line ({l}) as one that it owns.'.format(l=self.line)

    def __str__(self):
        return self.msg
