"""
The Plot Panel for the HKE Plotter program's main panel.
"""

import wx
import wx.lib.agw.ultimatelistctrl as ulc
from hkeplotter import HKEPlotterError


class PlotPanel(wx.Panel):
    """
    The plot creation panel.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY,
                          style=wx.WANTS_CHARS)

        self.fmf = self.GetTopLevelParent()
        self.plotter = self.fmf.plotter
        self.graphframe = self.fmf.graphframe

        self.create_sizers()
        self.populate_top()
        self.populate_middle()
        self.populate_bottom()

        self.bsMain.Layout()

    def create_sizers(self):
        """
        Create the sizers that control the overall structure of the
        panel.
        """
        self.bsMain = wx.BoxSizer(wx.VERTICAL)

        self.bsTop = wx.BoxSizer(wx.HORIZONTAL)
        self.bsMiddle = wx.BoxSizer(wx.HORIZONTAL)
        self.bsBottom = wx.BoxSizer(wx.HORIZONTAL)

        self.bsMain.Add(self.bsTop, 3, wx.EXPAND)
        self.bsMain.Add((5, 5))
        self.bsMain.Add(self.bsMiddle, 2, wx.EXPAND)
        self.bsMain.Add((5, 5))
        self.bsMain.Add(self.bsBottom, 2, wx.EXPAND)

        self.SetSizer(self.bsMain)
        self.bsMain.SetSizeHints(self)

    def populate_top(self, sizer=None):
        """
        Populate the top sizer.
        """
        if sizer is None:
            sizer = self.bsTop

        # listboxes
        bsFile, self.lboxFile = self.make_listbox('File')
        bsKey, self.lboxKey = self.make_listbox('Register')
        bsIndices, self.lboxIndices = self.make_listbox('Indices',
                                                        wx.LB_EXTENDED)

        # Tc checkbox and Plot button
        self.bsButtons = wx.BoxSizer(wx.VERTICAL)
        self.cbTcs = wx.CheckBox(self, wx.ID_ANY, "Show Tcs")
        self.cbTcs.SetValue(True)
        self.bPlot = wx.Button(self, wx.ID_ANY, "Plot")
        self.bsButtons.Add(self.cbTcs, 1, (wx.EXPAND | wx.ALIGN_BOTTOM |
                                           wx.ALIGN_CENTER_VERTICAL))
        self.bsButtons.Add(self.bPlot, 1, wx.EXPAND | wx.ALIGN_TOP)

        # Populate sizer
        sizer.Add(bsFile, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(bsKey, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(bsIndices, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.bsButtons, 0, wx.ALIGN_CENTER_VERTICAL)

        # Bind events
        self.Bind(wx.EVT_LISTBOX, self.onFileSelect, self.lboxFile)
        self.Bind(wx.EVT_LISTBOX, self.onKeySelect, self.lboxKey)
        self.Bind(wx.EVT_LISTBOX, self.onIndicesSelect, self.lboxIndices)
        self.Bind(wx.EVT_BUTTON, self.onPlot, self.bPlot)

        self.lboxFile.Bind(wx.EVT_KEY_UP, self.onKeyUpFile)
        self.lboxKey.Bind(wx.EVT_KEY_UP, self.onKeyUpKey)
        self.lboxIndices.Bind(wx.EVT_KEY_UP, self.onKeyUpIndices)

    def make_listbox(self, title, style=wx.LB_SINGLE):
        """
        A generator function for quickly constructing the listbox
        controls. Returns the sizer containing the statictext title
        and the listbox, and the listbox object itself.
        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        lblTitle = wx.StaticText(self, wx.ID_ANY, title,
                                 style=wx.ALIGN_CENTER)
        lbox = wx.ListBox(self, wx.ID_ANY, style=style)
        lbox.InsertItems(items=['No files loaded'], pos=0)

        sizer.Add(lblTitle, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(lbox, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        return sizer, lbox

    def clear_listbox(self, listbox):
        """
        Clear all of the items in a listbox.
        """
        num = listbox.GetCount()
        delrange = range(num-1, -1, -1)
        for i in delrange:
            listbox.Delete(i)

    def populate_middle(self, sizer=None):
        """
        Populate the middle sizer.
        """
        if sizer is None:
            sizer = self.bsMiddle

        self.lctrlLines = HKEListCtrl2(self)

        self.bsControls = wx.BoxSizer(wx.VERTICAL)
        self.bDelete = wx.Button(self, label='Delete')
        self.bClear = wx.Button(self, label='Clear All')
        self.bTc = wx.Button(self, label='Toggle Tc')
        self.bsControls.Add(self.bDelete, 1, wx.EXPAND)
        self.bsControls.Add(self.bClear, 1, wx.EXPAND)
        self.bsControls.Add(self.bTc, 1, wx.EXPAND)

        sizer.Add(self.lctrlLines, 1, wx.EXPAND)
        sizer.Add(self.bsControls, 0)

        self.Bind(wx.EVT_BUTTON, self.lctrlLines.onDelete,
                  self.bDelete)
        self.Bind(wx.EVT_BUTTON, self.lctrlLines.onClearAll,
                  self.bClear)
        self.Bind(wx.EVT_BUTTON, self.lctrlLines.onToggleTc,
                  self.bTc)

        sizer.SetSizeHints(self)

    def populate_bottom(self, sizer=None):
        """
        Populate the bottom sizer.
        """
        if sizer is None:
            sizer = self.bsBottom

        # X/Y scale radioboxes
        self.bsScale = wx.BoxSizer(wx.HORIZONTAL)
        choices = ('linear', 'log', 'symlog')
        self.rbXscale = wx.RadioBox(self, wx.ID_ANY,
                                    choices=choices,
                                    label='x-axis scale',
                                    style=wx.RA_SPECIFY_COLS,
                                    majorDimension=1)
        self.rbYscale = wx.RadioBox(self, wx.ID_ANY,
                                    choices=choices,
                                    label='y-axis scale',
                                    style=wx.RA_SPECIFY_COLS,
                                    majorDimension=1)
        self.lblXthresh = wx.StaticText(self, wx.ID_ANY,
                                        'X Thresh')
        self.lblYthresh = wx.StaticText(self, wx.ID_ANY,
                                        'Y Thresh')
        self.txtXthresh = wx.TextCtrl(self, wx.ID_ANY, '1.e-4')
        self.txtYthresh = wx.TextCtrl(self, wx.ID_ANY, '1.e-4')
        bsXthresh = wx.BoxSizer(wx.HORIZONTAL)
        bsYthresh = wx.BoxSizer(wx.HORIZONTAL)
        bsXthresh.Add(self.lblXthresh, 0, wx.EXPAND)
        bsXthresh.Add(self.txtXthresh, 1, wx.EXPAND)
        bsYthresh.Add(self.lblYthresh, 0, wx.EXPAND)
        bsYthresh.Add(self.txtYthresh, 1, wx.EXPAND)

        bsXscale = wx.BoxSizer(wx.VERTICAL)
        bsYscale = wx.BoxSizer(wx.VERTICAL)
        bsXscale.Add(self.rbXscale, 1, wx.EXPAND)
        bsXscale.Add(bsXthresh, 0, wx.EXPAND)
        bsYscale.Add(self.rbYscale, 1, wx.EXPAND)
        bsYscale.Add(bsYthresh, 0, wx.EXPAND)

        self.bsScale.Add(bsXscale, 1, wx.EXPAND)
        self.bsScale.Add(bsYscale, 1, wx.EXPAND)

        # Title and x/y labels
        self.bsTitleLabels = wx.BoxSizer(wx.VERTICAL)
        self.bsTitle = wx.BoxSizer(wx.HORIZONTAL)
        self.bsXlabel = wx.BoxSizer(wx.HORIZONTAL)
        self.bsYlabel = wx.BoxSizer(wx.HORIZONTAL)
        self.lblTitle = wx.StaticText(self, wx.ID_ANY, 'Title')
        self.lblXlabel = wx.StaticText(self, wx.ID_ANY, 'X Label')
        self.lblYlabel = wx.StaticText(self, wx.ID_ANY, 'Y Label')
        self.txtTitle = wx.TextCtrl(self, wx.ID_ANY)
        self.txtXlabel = wx.TextCtrl(self, wx.ID_ANY)
        self.txtYlabel = wx.TextCtrl(self, wx.ID_ANY)
        self.bsTitle.Add(self.lblTitle, 0, wx.EXPAND)
        self.bsTitle.Add(self.txtTitle, 1, wx.EXPAND)
        self.bsXlabel.Add(self.lblXlabel, 0, wx.EXPAND)
        self.bsXlabel.Add(self.txtXlabel, 1, wx.EXPAND)
        self.bsYlabel.Add(self.lblYlabel, 0, wx.EXPAND)
        self.bsYlabel.Add(self.txtYlabel, 1, wx.EXPAND)
        self.bsTitleLabels.Add(self.bsTitle, 0, wx.EXPAND)
        self.bsTitleLabels.Add(self.bsXlabel, 0, wx.EXPAND)
        self.bsTitleLabels.Add(self.bsYlabel, 0, wx.EXPAND)
        stline = wx.StaticLine(self, wx.ID_ANY,
                               style=wx.LI_HORIZONTAL)
        self.bsTitleLabels.Add(stline, 0, border=5,
                               flag=(wx.TOP | wx.BOTTOM | wx.EXPAND))

        # Legend toggle and selector
        self.chkLegend = wx.CheckBox(self, wx.ID_ANY, 'Legend')
        locs = ('None', 'Upper Right', 'Upper Left', 'Lower Left',
                'Lower Right', 'Right', 'Center Left', 'Center Right',
                'Lower Center', 'Upper Center', 'Center')
        self.choLegend = wx.Choice(self, wx.ID_ANY, choices=locs)

        self.bsTitleLabels.Add(self.chkLegend, 0, wx.EXPAND)
        self.bs3 = wx.BoxSizer(wx.HORIZONTAL)
        self.lblLegend = wx.StaticText(self, wx.ID_ANY, 'Location')
        self.bs3.Add(self.lblLegend, 0, wx.EXPAND)
        self.bs3.Add(self.choLegend, 1, wx.EXPAND)
        self.bsTitleLabels.Add(self.bs3, 0, wx.EXPAND)

        # Figure saving and storage
        self.bsFigs = wx.BoxSizer(wx.VERTICAL)
        self.lblFigName = wx.StaticText(self, wx.ID_ANY,
                                        'Figure Name')
        bsFigName = wx.BoxSizer(wx.HORIZONTAL)
        self.txtFigName = wx.TextCtrl(self, wx.ID_ANY, 'Figure')
        formats = ('.png', '.pdf', '.eps')
        self.choFigFormat = wx.Choice(self, wx.ID_ANY,
                                      choices=formats)
        self.choFigFormat.SetSelection(0)
        bsFigName.Add(self.txtFigName, 1, wx.EXPAND)
        bsFigName.Add(self.choFigFormat, 0, wx.EXPAND)
        self.chkSameAsTitle = wx.CheckBox(self, wx.ID_ANY,
                                          'Same as Title')
        self.chkSameAsTitle.SetValue(True)
        self.bFigSave = wx.Button(self, label='Save Figure to Disk')
        self.bFigStore = wx.Button(self,
                                   label='Store Figure in Buffer')
        self.bFigStore.Enable(False)
        self.bsFigs.Add(self.lblFigName, 0, wx.EXPAND)
        self.bsFigs.Add(bsFigName, 0, wx.EXPAND)
        self.bsFigs.Add(self.chkSameAsTitle, 0, wx.EXPAND)
        self.bsFigs.Add((5, 5))
        self.bsFigs.Add(self.bFigSave, 0, wx.EXPAND)
        self.bsFigs.Add((5, 5))
        self.bsFigs.Add(self.bFigStore, 0, wx.EXPAND)

        # Add them all to the general sizer
        sizer.Add(self.bsScale, 0, wx.EXPAND)
        sizer.Add(self.bsTitleLabels, 1, wx.EXPAND)
        sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0,
                  border=5, flag=(wx.LEFT | wx.RIGHT | wx.EXPAND))
        sizer.Add(self.bsFigs, 1, wx.EXPAND)

        # Bind X/Y scale radioboxes
        self.Bind(wx.EVT_RADIOBOX, self.onXscale, self.rbXscale)
        self.Bind(wx.EVT_RADIOBOX, self.onYscale, self.rbYscale)

        # Bind legend toggle and selector
        self.Bind(wx.EVT_CHECKBOX, self.onLegendToggle, self.chkLegend)
        self.Bind(wx.EVT_CHOICE, self.onLegendSelect, self.choLegend)

        # Bind titles/labels
        self.Bind(wx.EVT_TEXT, self.onTitle, self.txtTitle)
        self.Bind(wx.EVT_TEXT, self.onXlabel, self.txtXlabel)
        self.Bind(wx.EVT_TEXT, self.onYlabel, self.txtYlabel)

        # Bind figure stuff
        self.Bind(wx.EVT_TEXT, self.onFigName, self.txtFigName)
        self.Bind(wx.EVT_CHECKBOX, self.onSameAsTitle,
                  self.chkSameAsTitle)
        self.Bind(wx.EVT_BUTTON, self.onSaveFig, self.bFigSave)
        self.Bind(wx.EVT_BUTTON, self.onStoreFig, self.bFigStore)

    def update_model(self):
        """
        Updates the listboxes to reflect the updated model.
        """
        lboxes = [self.lboxFile, self.lboxKey, self.lboxIndices]
        for lbox in lboxes:
            self.clear_listbox(lbox)

        model = self.fmf.model
        dfnames = model.keys()
        if not dfnames:
            for lbox in lboxes:
                lbox.InsertItems(['No files loaded'], pos=0)
            return

        self.lboxFile.InsertItems(dfnames, 0)
        self.Refresh()

    def onFileSelect(self, event):
        model = self.fmf.model
        name = event.GetString()
        df = model[name]
        dewar = df['dewar']
        if dewar == 'shiny':
            allowed = ['Side 1 Resistances',
                       'Side 2 Resistances',
                       'Side 1 Excitation Currents',
                       'Side 2 Excitation Currents']
                       # 'Thermometer Excitation Current']
        elif dewar == 'craac':
            allowed = ['Side 1 Resistances',
                       'Side 1 Excitation Currents']
                       # 'Thermometer Excitation Current']
        self.clear_listbox(self.lboxKey)
        self.lboxKey.InsertItems(allowed, 0)

    def onKeySelect(self, event):
        model = self.fmf.model
        register = event.GetString()
        name = self.lboxFile.GetStringSelection()

        self.clear_listbox(self.lboxIndices)

        if register == 'Thermometer Excitation Current':
            self.lboxIndices.InsertItems(['Thermometer'], 0)
            return

        side = register.split()[1]
        ds = model[name]['Side {s} Descriptions'.format(s=side)]
        ds = ['Ch {i} - {d}'.format(i=i, d=d)
              for i, d in enumerate(ds)]
        self.lboxIndices.InsertItems(ds, 0)

    def onIndicesSelect(self, event):
        pass

    def onPlot(self, event):
        """
        When you press the plot button...
        """
        plotter = self.fmf.plotter
        graphframe = self.fmf.graphframe

        model = self.fmf.model
        name = self.lboxFile.GetStringSelection()
        register = self.lboxKey.GetStringSelection()
        df = model[name]
        dewar = df['dewar']

        try:
            side = register.split()[1]
            descriptions = df['Side {i} Descriptions'.format(i=side)]
        except KeyError:
            descriptions = ['Thermometer']
        except IndexError:
            return

        xlabel = 'Temperature (K)'
        plotter.xlabel(xlabel)
        self.txtXlabel.ChangeValue(xlabel)
        if 'Resistances' in register:
            ylabel = 'Resistance ($\Omega$)'
            plotter.ylabel(ylabel)
            self.txtYlabel.ChangeValue(ylabel)
        elif 'Currents' in register:
            ylabel = 'Excitation Current (nA)'
            plotter.ylabel(ylabel)
            self.txtYlabel.ChangeValue(ylabel)

        indices = self.lboxIndices.GetSelections()
        tcflag = self.cbTcs.GetValue()

        for i in indices:
            i = int(i)
            d = descriptions[i]
            linedict = plotter.RvsTPlot(df, register, i,
                                        Tcline=tcflag)
            # n = self.lctrlLines.GetItemCount()
            row = [register, name, dewar,
                   'Ch {i} - {d}'.format(i=i, d=d)]
            self.lctrlLines.Append(row)
            self.lctrlLines.linelist.append(linedict)
        self.lctrlLines.adjustColumnSizes()

        graphframe.replace_figure(plotter.figure)

    def onKeyUpFile(self, event):
        # Not functioning for some reason...
        # print "in onKeyUpFile"
        # pressed = event.GetKeyCode()
        # rightkeys = (wx.WXK_RIGHT,)
        # if pressed in rightkeys:
        #     print "in pressed" #DELME
        #     self.bPlot.SetFocus()
        #     return
        # event.Skip()
        pass

    def onKeyUpKey(self, event):
        pass

    def onKeyUpIndices(self, event):
        pass

    def onXscale(self, event):
        scaledict = {0: 'linear', 1: 'log', 2: 'symlog'}
        selected = event.GetInt()
        newscale = scaledict[selected]
        try:
            linthreshx = float(self.txtXthresh.GetValue())
        except ValueError:
            linthreshx = 1.e-4
            self.txtXthresh.ChangeValue('1.e-4')
            self.txtXthresh.SetInsertionPoint(-1)
        self.plotter.xscale(newscale, linthreshx=linthreshx)
        self.plotter.autorange()
        self.graphframe.replace_figure(self.plotter.figure)

    def onYscale(self, event):
        scaledict = {0: 'linear', 1: 'log', 2: 'symlog'}
        selected = event.GetInt()
        newscale = scaledict[selected]
        try:
            linthreshy = float(self.txtYthresh.GetValue())
        except ValueError:
            linthreshy = 1.e-4
            self.txtYthresh.ChangeValue('1.e-4')
            self.txtYthresh.SetInsertionPoint(-1)
        self.plotter.yscale(newscale, linthreshy=linthreshy)
        self.plotter.autorange()
        self.graphframe.replace_figure(self.plotter.figure)

    def onLegendToggle(self, event):
        checked = event.IsChecked()
        if checked:
            loc = self.choLegend.GetSelection()
            if loc == 0:
                loc = 1
                self.choLegend.SetSelection(loc)
            self.plotter.legend(loc=loc)
        else:
            self.plotter.hide_legend()
        self.graphframe.replace_figure(self.plotter.figure)

    def onLegendSelect(self, event):
        loc = self.choLegend.GetSelection()
        if loc == 0:
            self.chkLegend.SetValue(False)
            self.plotter.hide_legend()
        else:
            self.chkLegend.SetValue(True)
            self.plotter.legend(loc=loc)
        self.graphframe.replace_figure(self.plotter.figure)

    def onTitle(self, event):
        title = event.GetString()
        sameas = self.chkSameAsTitle.GetValue()
        if sameas:
            self.txtFigName.ChangeValue(title)
        self.plotter.title(title)
        self.graphframe.replace_figure(self.plotter.figure)

    def onXlabel(self, event):
        xlabel = event.GetString()
        self.plotter.xlabel(xlabel)
        self.graphframe.replace_figure(self.plotter.figure)

    def onYlabel(self, event):
        ylabel = event.GetString()
        self.plotter.ylabel(ylabel)
        self.graphframe.replace_figure(self.plotter.figure)

    def onFigName(self, event):
        self.chkSameAsTitle.SetValue(False)

    def onSameAsTitle(self, event):
        checked = event.IsChecked()
        if checked:
            title = self.txtTitle.GetValue()
            self.txtFigName.ChangeValue(title)
            self.txtFigName.SetInsertionPoint(len(title))

    def onSaveFig(self, event):
        figname = self.txtFigName.GetValue()
        if figname == '':
            figname = 'Figure'
        form = self.choFigFormat.GetStringSelection()
        tosave = figname + form
        self.plotter.savefig(tosave, dpi=300)

    def onStoreFig(self, event):
        pass


class HKEListCtrl2(ulc.UltimateListCtrl):
    """
    The list control for displaying the loaded data files.
    """
    def __init__(self, parent):
        ulc.UltimateListCtrl.__init__(self, parent, wx.ID_ANY,
            agwStyle = (wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES |
                        wx.LC_SINGLE_SEL |
                        ulc.ULC_HAS_VARIABLE_ROW_HEIGHT))

        self.fmf = self.GetTopLevelParent()

        self.linelist = []

        self.make_columns()
        self.make_context_menu()

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect, self)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect, self)

    def make_columns(self):
        columnlist = ['Register', 'Filename', 'Dewar', 'Description']
        for i, label in enumerate(columnlist):
            self.InsertColumn(i, label)

    def make_context_menu(self):
        self.mContextMenu = wx.Menu()
        # self.miListChs = self.mContextMenu.Append(wx.ID_ANY,
        #                                 'List/Modify Channels')
        # self.miRename = self.mContextMenu.Append(wx.ID_ANY, 'Rename')
        # self.miChangeDesc = self.mContextMenu.Append(wx.ID_ANY,
        #                                    'Change Description')
        self.miDelete = self.mContextMenu.Append(wx.ID_ANY,
                                                 'Delete Item')
        self.miTc = self.mContextMenu.Append(wx.ID_ANY,
                                             'Toggle Tc Line')

        # self.Bind(ulc.EVT_LIST_COL_RIGHT_CLICK, self.onContextMenu,
        #           self)
        self.Bind(wx.EVT_RIGHT_UP, self.onContextMenu)
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.onContextMenu)
        # self.Bind(wx.EVT_MENU, self.onRename, self.miRename)
        # self.Bind(wx.EVT_MENU, self.onChangeDesc, self.miChangeDesc)
        self.Bind(wx.EVT_MENU, self.onDelete, self.miDelete)
        self.Bind(wx.EVT_MENU, self.onToggleTc, self.miTc)

    def onContextMenu(self, event):
        self.PopupMenu(self.mContextMenu)

    def deleteLine(self, rowindex):
        """
        Delete a line from the list and from the plotter, specified by
        the row index.
        """
        plotter = self.fmf.plotter
        graphframe = self.fmf.graphframe
        line = self.linelist[rowindex]
        try:
            plotter.delete_line(line)
            self.DeleteItem(rowindex)
            del self.linelist[rowindex]
            graphframe.replace_figure(plotter.figure)
        except HKEPlotterError:
            pass

    def toggleTc(self, rowindex):
        """
        Toggle the Tc line on and off on the line specified by row
        index.
        """
        plotter = self.fmf.plotter
        graphframe = self.fmf.graphframe
        line = self.linelist[rowindex]
        if line['vlines']:
            plotter.delTcline(line)
        else:
            plotter.addTcline(line)
        graphframe.replace_figure(plotter.figure)

    def highlightLine(self, rowindex):
        """
        Highlight the line identified by the rowindex and update the
        figure.
        """
        plotter = self.fmf.plotter
        graphframe = self.fmf.graphframe

        line = self.linelist[rowindex]
        plotter.highlight_line(line)
        graphframe.replace_figure(plotter.figure)

    def unhighlightLine(self, rowindex):
        """
        Unhighlight the line identified by the rowindex and update the
        figure.
        """
        plotter = self.fmf.plotter
        graphframe = self.fmf.graphframe

        line = self.linelist[rowindex]
        plotter.unhighlight_line(line)
        graphframe.replace_figure(plotter.figure)

    def onDelete(self, event):
        selected = self.GetFirstSelected()
        self.deleteLine(selected)

    def onClearAll(self, event):
        n = self.GetItemCount()
        nr = range(n)
        nr.reverse()
        for i in nr:
            self.deleteLine(i)

    def onDeselect(self, event):
        row = event.m_itemIndex
        self.unhighlightLine(row)

    def onSelect(self, event):
        row = event.m_itemIndex #DELME?
        self.highlightLine(row)

    def onToggleTc(self, event):
        selected = self.GetFirstSelected()
        self.toggleTc(selected)

    def insert_test_data(self):
        """
        Insert some toy data for testing into the columns.
        """
        data = [['file1', 'hke_2013file1.dat', 'shiny',
                 'a description!'],
                 ['file2', 'hke_2013file2.dat', 'craac',
                  'descriptoin a']]
        for row in data:
            self.Append(row)

    def adjustColumnSizes(self):
        """
        Reassess and adjust all the column sizes so they fit
        correctly.
        """
        numcol = self.GetColumnCount()
        for col in range(numcol):
            self.setColumnWidthAuto(col)

    def setColumnWidthAuto(self, column):
        """
        Sets the column width to the largest of the header info or the
        largest item in the column.
        """
        colnum = self.GetColumnCount()

        if (column + 1) == colnum:
            # -3 -> LIST_AUTOSIZE_FILL; doesn't seem to work
            self.SetColumnWidth(column, 300)  # -3)
            return

        # Try the header size
        self.SetColumnWidth(column, wx.LIST_AUTOSIZE_USEHEADER)
        hsize = self.GetColumnWidth(column)

        # Try the item size
        self.SetColumnWidth(column, wx.LIST_AUTOSIZE)
        isize = self.GetColumnWidth(column)

        # Pick whichever is bigger; needs the +25 since the size
        # doesn't seem to be estimated correctly
        size = max(hsize, isize) + 25
        self.SetColumnWidth(column, size)
