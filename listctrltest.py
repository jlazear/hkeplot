import wx
import wx.lib.mixins.listctrl as listmix

class TestListCtrl(wx.ListCtrl):
    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style)

class TestListCtrlPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)

        self.initialize_list()

        self.bsMain = wx.BoxSizer(wx.VERTICAL)

        self.bsMain.Add(self.list, 1, wx.EXPAND)

    def initialize_list(self):
        self.list.InsertColumn(0, 'Artist')
        self.list.InsertColumn(1, 'Title')
        self.list.InsertColumn(2, 'Genre')

class TestListCtrlFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'TestListCtrlFrame')

        bs = wx.BoxSizer(wx.VERTICAL)

        lctrl = TestListCtrlPanel(self)

        bs.Add(lctrl, 1, wx.EXPAND)

        self.SetSizer(bs)

        self.Layout()

class TestListCtrlApp(wx.App):
    def OnInit(self):
        #        wx.InitAllImageHandlers()
        fListCtrlFrame = TestListCtrlFrame()
        fListCtrlFrame.Show()
        self.fListCtrlFrame = fListCtrlFrame
        return 1
