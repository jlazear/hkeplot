"""
The Graph Frame for the HKE Plotter program.
"""
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


class GraphFrame(wx.Frame):
    """
    The plot frame
    """
    title = 'HKE Plot'

    def __init__(self):
        styles = (wx.RESIZE_BORDER | wx.MINIMIZE_BOX)
        # wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
        #                   title=self.title, style=styles)
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          title=self.title, style=styles)

        self.panel = wx.Panel(self)
        bsPlot, cPlot, tbPlot = self.create_plot_box(self.panel)

        self.bsPlot = bsPlot
        self.cPlot = cPlot
        self.tbPlot = tbPlot

        self.bs2 = wx.BoxSizer(wx.HORIZONTAL)
        self.bs2.Add(self.bsPlot, 1, wx.EXPAND)

        self.panel.SetSizer(self.bs2)
        self.bs2.Fit(self)

        self.Bind(wx.EVT_CLOSE, self.onClose, self)

    def create_plot_box(self, parent, plotsize=(6., 4.), data=None,
                        tb=True, figure=None):
        """
        Creates the panel containing the graph.

        data is a 2 x N element array where the first row contains the
        x data and the second row contains the y data. Passing in None
        will insert no data.

        The tb flag determines whether or not to create the associated
        toolbar for the figure.

        The figure arguments allows you to specify a figure to insert
        into the FigureCanvas object. If None is passed, it creates a
        defualt one.

        This method creates and returns a vertical BoxSizer (bsPlot),
        with the plot on top and the toolbar associated with the plot
        on bottom. Also returns the FigureCanvas object (canvas) and
        the toolbar object (toolbar).
        """
        if figure is None:
            fig, axes, lines = self.init_plot(plotsize, data)
        else:
            fig = figure
            axes = fig.axes
            lines = [ax.lines for ax in axes]

        canvas = FigCanvas(parent, -1, fig)

        bsPlot = wx.BoxSizer(wx.VERTICAL)
        bsPlot.Add(canvas, 1, flag=wx.GROW)

        if tb:
            toolbar = NavigationToolbar(canvas)
            toolbar.Realize()
            bsPlot.Add(toolbar, 0, wx.LEFT | wx.EXPAND)
        else:
            toolbar = None

        return bsPlot, canvas, toolbar

    def init_plot(self, plotsize=(6., 4.), data=None):
        fig = Figure(plotsize, dpi=100)

        axes = fig.add_subplot(111)

        if data is not None:
            xs, ys = data
            lines = [axes.plot(xs, ys)]
        else:
            lines = [[]]

        return fig, axes, lines

    def replace_figure(self, newfigure, oldsizer=None):
        """
        Replaces the figure contained the oldsizer, which is assumed
        to be a figure + toolbar combination contained in a sizer, as
        created by create_plot_box, with the newly specified figure
        and its associated toolbar.

        Note that this function only works if the figure's sizer is
        the only object that is in oldsizer, because wxPython does not
        seem interested in removing items by name.

        The old sizer object is deleted.
        """
        if oldsizer is None:
            oldsizer = self.bs2

        self.cPlot.Destroy()
        self.tbPlot.Destroy()

        bsPlot, cPlot, tbPlot = self.create_plot_box(self.panel,
                                                     figure=newfigure)

        self.bsPlot = bsPlot
        self.cPlot = cPlot
        self.tbPlot = tbPlot

        oldsizer.Add(bsPlot, 1, wx.EXPAND)
        oldsizer.Remove(0)

        oldsizer.Layout()

    def onClose(self, event):
        pass
