import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
import wx
from graphframe import GraphFrame
from modelpanel import ModelPanel
from plotpanel import PlotPanel
from hkeplotter import HKEPlotter as Plotter
from hkeplotmodel import HKEModel as Model
from hkeconfig import HKEConfig


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
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging)

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
    def __init__(self, graphframe=None, model=None, plotter=None,
                 configname='.hkeplot'):
        wx.Frame.__init__(self, None, wx.ID_ANY, "HKE Plotter",
                          size=(700, 500))

        self.model = model
        self.graphframe = graphframe
        self.plotter = plotter
        self.config = HKEConfig(configname)

        self.make_menubar()

        self.panel = wx.Panel(self)

        self.notebook = NotebookFrame(self.panel)

        self.bsMain = wx.BoxSizer(wx.VERTICAL)
        self.bsMain.Add(self.notebook, 1, wx.ALL | wx.EXPAND)

        self.panel.SetSizer(self.bsMain)

        self.Layout()

        self.Bind(wx.EVT_CLOSE, self.onClose, self)

    def make_menubar(self):
        self.menuBar = wx.MenuBar()
        self.menus = []

        self.mFile = wx.Menu()
        self.miQuit = self.mFile.Append(wx.ID_EXIT, '&Quit', 'Quit')
        self.menus.append(self.mFile)

        self.menuBar.Append(self.mFile, "&File")

        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.onClose, self.miQuit)

    def add_model(self, model):
        self.model = model

    def add_plotter(self, plotter):
        self.plotter = plotter

    def add_graphframe(self, graphframe):
        self.graphframe = graphframe
        self.notebook.plotpanel.graphframe = graphframe

    def onClose(self, event):
        # self.save_config()

        self.graphframe.Destroy()
        self.Destroy()


class GraphApp(wx.App):
    def OnInit(self):
        # Make the model and plotter, but do not initialize
        self.model = Model()
        self.plotter = Plotter(self.model)

        # Make the MainFrame and GraphFrame
        fMainFrame = MainFrame(model=self.model,
                               plotter=self.plotter)
        fMainFrame.Show()
        self.SetTopWindow(fMainFrame)
        self.fMainFrame = fMainFrame

        fGraphFrame = GraphFrame()
        fGraphFrame.Show()
        self.fGraphFrame = fGraphFrame

        # Attach the GraphFrame to the MainFrame
        fMainFrame.add_graphframe(self.fGraphFrame)

        # Initialize plotter figure
        # Note this must be done after GraphFrame is created, since it
        # has a tendency to create a frame of its own if none exists.
        self.plotter.makefigure()
        self.plotter.add_subplot(111)

        return 1

if __name__ == '__main__':
    app = GraphApp(0)
    app.MainLoop()
