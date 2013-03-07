import wx
from graphframe import GraphFrame
from modelpanel import ModelPanel
from plotpanel import PlotPanel
from hkeplotter import HKEPlotter as Plotter
from hkeplotmodel import HKEModel as Model

import numpy as np


class NotebookFrame(wx.Notebook):
    """
    The notebook frame.
    """
    def __init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT):
        wx.Notebook.__init__(self, parent, id=id, style=style)

        self.modelpanel = ModelPanel(self)
        self.plotpanel = PlotPanel(self)

        self.AddPage(self.modelpanel, "Data files")
        self.AddPage(self.plotpanel, "Plot")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)

    def onPageChanging(self, event):
        new = event.GetSelection()
        if new == 1:
            self.plotpanel.update_model()

        # Necessary to actually cause page change
        event.Skip()


class MainFrame(wx.Frame):
    """
    The main frame that holds all of the others. Really just an
    expandable container for the notebook.
    """
    def __init__(self, graphframe=None, model=None, plotter=None):
        wx.Frame.__init__(self, None, wx.ID_ANY, "HKE Plotter",
                          size=(700, 500))

        self.model = model
        self.graphframe = graphframe
        self.plotter = plotter

        self.make_menubar()

        self.panel = wx.Panel(self)

        self.notebook = NotebookFrame(self.panel)

        self.bsMain = wx.BoxSizer(wx.VERTICAL)
        self.bsMain.Add(self.notebook, 1, wx.ALL|wx.EXPAND)

        self.panel.SetSizer(self.bsMain)

        self.Layout()

    def make_menubar(self):

        ## WHY DOESN'T THIS WORK? ## #DELME
        self.menuBar = wx.MenuBar()
        self.menus = []

        mFile = wx.Menu()
        mFile.Append(wx.ID_EXIT, '&Quit', 'Quit')
        self.menus.append(mFile)

        self.menuBar.Append(mFile, "&File")

        self.SetMenuBar(self.menuBar)

    def add_model(self, model):
        self.model = model

    def add_plotter(self, plotter):
        self.plotter = plotter

    def add_graphframe(self, graphframe):
        self.graphframe = graphframe


class GraphApp(wx.App):
    def OnInit(self):
        # Make the model and plotter
        self.model = Model()
        self.plotter = Plotter(self.model)
        self.plotter.makefigure()
        self.plotter.add_subplot(111)

        fGraphFrame = GraphFrame()
        # self.SetTopWindow(fGraphFrame)
        fGraphFrame.Show()
        self.fGraphFrame = fGraphFrame

        fMainFrame = MainFrame(graphframe=self.fGraphFrame,
                                  model=self.model,
                                  plotter=self.plotter)
        fMainFrame.Show()
        self.fMainFrame = fMainFrame
        return 1

if __name__ == '__main__':
    app = GraphApp(0)
    app.MainLoop()
