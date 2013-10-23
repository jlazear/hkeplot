"""
The Model Panel for the HKE Plotter program's main panel.
"""
import wx
import wx.lib.filebrowsebutton as wxfbb
import wx.lib.agw.ultimatelistctrl as ulc
from hkeplotmodel import HKEPlotError
from hkeconfig import HKEConfig
from HKEBinaryLibrary import HKEBinaryError


class ModelPanel(wx.Panel):
    """
    The data management panel.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.fmf = self.GetTopLevelParent()
        self.config = self.fmf.config

        self.create_sizers()
        self.populate_bottom()
        self.populate_top()
        self.preload_files()

    def create_sizers(self):
        """
        Create the sizers in the panel.
        """
        self.bsMain = wx.BoxSizer(wx.VERTICAL)

        self.bsTop = wx.BoxSizer(wx.HORIZONTAL)
        self.bsBottom = wx.BoxSizer(wx.HORIZONTAL)

        self.bsMain.Add(self.bsTop, 4, wx.EXPAND)
        self.bsMain.Add(self.bsBottom, 1, wx.EXPAND)

        self.SetSizer(self.bsMain)

    def populate_top(self, sizer=None):
        """
        Populate the top sizer.
        """
        if sizer is None:
            sizer = self.bsTop

        self.lctrlData = HKEListCtrl(self)

        self.bsControls = wx.BoxSizer(wx.VERTICAL)
        # self.bList = wx.Button(self, label='List')
        self.bRename = wx.Button(self, label='Rename')
        self.bChange = wx.Button(self, label='Desc')
        self.bDelete = wx.Button(self, label='Delete')
        # self.bsControls.Add(self.bList, 1, wx.EXPAND)
        self.bsControls.Add(self.bRename, 1, wx.EXPAND)
        self.bsControls.Add(self.bChange, 1, wx.EXPAND)
        self.bsControls.Add(self.bDelete, 1, wx.EXPAND)

        sizer.Add(self.lctrlData, 1, wx.EXPAND)
        sizer.Add(self.bsControls, 0)

        # self.Bind(wx.EVT_BUTTON, self.lctrlData.onListChs, self.bList)
        self.Bind(wx.EVT_BUTTON, self.lctrlData.onRename,
                  self.bRename)
        self.Bind(wx.EVT_BUTTON, self.lctrlData.onChangeDesc,
                  self.bChange)
        self.Bind(wx.EVT_BUTTON, self.lctrlData.onDelete,
                  self.bDelete)

    def populate_bottom(self, sizer=None):
        """
        Populate the bottom sizer.
        """
        if sizer is None:
            sizer = self.bsBottom

        self.bsLoad = wx.BoxSizer(wx.VERTICAL)

        self.fbbFileBrowser = wxfbb.FileBrowseButton(self, -1,
            labelText='Data File')
        datafolder = self.config['hkeplot']['datafolder']
        print "datafolder = ", datafolder #DELME
        self.fbbFileBrowser.SetValue(datafolder)

        self.fbbCalFileBrowser = wxfbb.FileBrowseButton(self, -1,
            labelText='Cal File')
        calfolder = self.config['hkeplot']['calfolder']
        self.fbbCalFileBrowser.SetValue(calfolder)

        self.bsBoards = wx.BoxSizer(wx.HORIZONTAL)
        self.bsBoardsButtons = wx.BoxSizer(wx.VERTICAL)
        self.lblOverwrite = wx.StaticText(self, -1,
                                          label='Use stored if available')
        self.chkOverwrite = wx.CheckBox(self, -1)
        self.chkOverwrite.SetValue(True)
        self.bsBoardsButtons.Add(self.lblOverwrite, 0, wx.ALIGN_CENTER)
        self.bsBoardsButtons.Add(self.chkOverwrite, 0, wx.ALIGN_CENTER)

        self.fbbBoardFileBrowser = wxfbb.FileBrowseButton(self, -1,
            labelText='Boards File')
        boardsfolder = self.config['hkeplot']['boardsfolder']
        self.fbbBoardFileBrowser.SetValue(boardsfolder)
        self.bsBoards.Add(self.bsBoardsButtons, 0, wx.EXPAND | wx.RIGHT)
        self.bsBoards.Add(self.fbbBoardFileBrowser, 1, wx.EXPAND | wx.LEFT)

        self.bLoad = wx.Button(self, -1, label='Load file')

        self.bsLoad.Add(self.fbbFileBrowser, 1, wx.EXPAND | wx.BOTTOM)
        self.bsLoad.Add(self.fbbCalFileBrowser, 1,
                        wx.EXPAND | wx.BOTTOM)
        self.bsLoad.Add(self.bsBoards, 1, wx.EXPAND | wx.BOTTOM)
        self.bsLoad.Add(self.bLoad, 1, wx.EXPAND | wx.TOP)

        sizer.Add(self.bsLoad, 1, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.onLoadButton, self.bLoad)
        self.Bind(wx.EVT_CHECKBOX, self.onOverwriteCheckBox,
                  self.chkOverwrite)

    def onLoadButton(self, event):
        # Load the specified file into the model
        model = self.fmf.model
        fname = self.fbbFileBrowser.GetValue()
        calfname = self.fbbCalFileBrowser.GetValue()
        overwrite = self.chkOverwrite.IsChecked()
        if overwrite:
            boardfname = self.fbbBoardFileBrowser.GetValue()
        else:
            boardfname = None
        try:
            model.loadfile(fname, calfname, bcfgfile=boardfname,
                           handleerrors=False)
        except (HKEPlotError, HKEBinaryError) as e:
            errtxt = str(e)
            dlg = wx.MessageDialog(self, errtxt,
                                   "Failed to load file",
                                   (wx.OK | wx.ICON_INFORMATION))
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Update the listctrl with the newly added data file
        name = model.keys()[-1]
        df = model[name]
        fname2 = df['filename']
        dewar = df['dewar']
        description = df['description']
        row = [name, fname2, dewar, description]
        self.lctrlData.Append(row)
        HKEConfig.add_loaded_file(df, name=name)

        self.adjustColumnSizes()

    def onOverwriteCheckBox(self, event):
        """
        Warn the user that will overwrite and destroy old boards.txt
        config file if present.
        """
        if not event.IsChecked():
            msg = ("WARNING: If a data file with a pre-existing boards.txt"
                   " file is loaded, the stored boards.txt file will be "
                   "overwritten and destroyed! Make sure you REALLY want to"
                   " overwrite the stored file!")
            dlg = wx.MessageDialog(self, msg, 'WARNING!', wx.OK)
            dlg.ShowModal()
            dlg.Destroy()


    def preload_files(self, configfname='.hkeplot'):
        """
        Load the files specified in the config file.
        """
        model = self.fmf.model
        fdict = HKEConfig.get_loaded_files(configfname)

        for fname, d in fdict.items():
            propername = d['proper name']
            absname = d['data file']
            calname = d['cal file']
            dewar = d['dewar']
            desc = d['description']
            taddress = int(d['temperature address'])
            tchannel = int(d['temperature channel'])
            try:
                model.loadfile(absname, calname, description=desc,
                               taddress=taddress, tchannel=tchannel)
                model.rename(-1, propername)

                # Update the listctrl with the newly added data file
                name = model.keys()[-1]
                df = model[name]
                fname2 = df['filename']
                dewar = df['dewar']
                description = df['description']
                row = [name, fname2, dewar, description]
                self.lctrlData.Append(row)

                self.adjustColumnSizes()
            except (HKEPlotError, HKEBinaryError) as e:
                errtxt = str(e)
                dlg = wx.MessageDialog(self, errtxt,
                                       "Failed to load file",
                                       (wx.OK | wx.ICON_INFORMATION))
                dlg.ShowModal()
                dlg.Destroy()

    def adjustColumnSizes(self):
        """
        Reassess and adjust all the column sizes so they fit
        correctly.
        """
        numcol = self.lctrlData.GetColumnCount()
        for col in range(numcol):
            self.setColumnWidthAuto(col)

    def setColumnWidthAuto(self, column):
        """
        Sets the column width to the largest of the header info or the
        largest item in the column.
        """
        colnum = self.lctrlData.GetColumnCount()

        if (column + 1) == colnum:
            # -3 -> LIST_AUTOSIZE_FILL; doesn't seem to work
            self.lctrlData.SetColumnWidth(column, 300)  # -3)
            return

        # Try the header size
        self.lctrlData.SetColumnWidth(column,
                                      wx.LIST_AUTOSIZE_USEHEADER)
        hsize = self.lctrlData.GetColumnWidth(column)

        # Try the item size
        self.lctrlData.SetColumnWidth(column, wx.LIST_AUTOSIZE)
        isize = self.lctrlData.GetColumnWidth(column)

        # Pick whichever is bigger; needs the +25 since the size
        # doesn't seem to be estimated correctly
        size = max(hsize, isize) + 25
        self.lctrlData.SetColumnWidth(column, size)


class HKEListCtrl(ulc.UltimateListCtrl):
    """
    The list control for displaying the loaded data files.
    """
    def __init__(self, parent):
        ulc.UltimateListCtrl.__init__(self, parent, wx.ID_ANY,
            agwStyle=(wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES |
                      wx.LC_SINGLE_SEL |
                      ulc.ULC_HAS_VARIABLE_ROW_HEIGHT))

        self.fmf = self.GetTopLevelParent()
        self.parent = parent

        self.make_columns()
        self.make_context_menu()

    def make_columns(self):
        columnlist = ['Data file', 'Filename', 'Dewar', 'Description']
        for i, label in enumerate(columnlist):
            self.InsertColumn(i, label)

    def make_context_menu(self):
        self.mContextMenu = wx.Menu()
        self.miListChs = self.mContextMenu.Append(wx.ID_ANY,
                                        'List/Modify Channels')
        self.miRename = self.mContextMenu.Append(wx.ID_ANY, 'Rename')
        self.miChangeDesc = self.mContextMenu.Append(wx.ID_ANY,
                                           'Change Description')
        self.miDelete = self.mContextMenu.Append(wx.ID_ANY,
                                                 'Delete Item')
        self.miChangeRegisters = self.mContextMenu.Append(wx.ID_ANY,
                                             'Change Registers')

        # self.Bind(ulc.EVT_LIST_COL_RIGHT_CLICK, self.onContextMenu,
        #           self)
        self.Bind(wx.EVT_RIGHT_UP, self.onContextMenu)
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.onContextMenu)
        self.Bind(wx.EVT_MENU, self.onRename, self.miRename)
        self.Bind(wx.EVT_MENU, self.onChangeDesc, self.miChangeDesc)
        self.Bind(wx.EVT_MENU, self.onDelete, self.miDelete)
        # self.Bind(wx.EVT_MENU, self.onListChs, self.miListChs)
        self.Bind(wx.EVT_MENU, self.onChangeReg,
                  self.miChangeRegisters)

    def onContextMenu(self, event):
        self.PopupMenu(self.mContextMenu)

    def onRename(self, event):
        selected = self.GetFirstSelected()
        item = self.GetItem(selected, 0)
        name = item.GetText()
        model = self.fmf.model

        dlg = wx.TextEntryDialog(self, 'Insert new name:',
                                 'Rename data model item', name)

        if dlg.ShowModal() == wx.ID_OK:
            newname = dlg.GetValue()
        else:
            return

        try:
            model.rename(name, newname)
            df = model[newname]
            HKEConfig.remove_loaded_file(name=name)
            HKEConfig.add_loaded_file(df, name=newname)
            self.SetStringItem(selected, 0, newname)
        except ValueError:
            print "Item not found in model!"

    def onChangeDesc(self, event):
        selected = self.GetFirstSelected()
        item = self.GetItem(selected, 3)
        name = self.GetItem(selected, 0).GetText()
        description = item.GetText()
        model = self.fmf.model
        try:
            df = model[name]
        except KeyError:
            pass

        dlg = wx.TextEntryDialog(self, 'Insert new description:',
                                 'Change description', description)

        if dlg.ShowModal() == wx.ID_OK:
            newdescription = dlg.GetValue()
        else:
            return

        try:
            df['description'] = newdescription
            self.SetStringItem(selected, 3, newdescription)
            HKEConfig.add_loaded_file(df, name=name)
        except NameError:
            print "Item not found in model!"

    def onDelete(self, event):
        selected = self.GetFirstSelected()
        item = self.GetItem(selected, 0)
        name = item.GetText()
        model = self.fmf.model
        try:
            del model[name]
            self.DeleteItem(selected)
            HKEConfig.remove_loaded_file(name=name)
        except KeyError:
            pass

    #DELME: NEEDS TO BE UPDATED TO NEW METADATA FORMAT!
    # def onListChs(self, event):
    #     selected = self.GetFirstSelected()
    #     name = self.GetItem(selected, 0).GetText()
    #     model = self.fmf.model

    #     dlg = ChannelsDialog(self, wx.ID_ANY, name, model,
    #                          title="Channels List")

    #     dlg.CenterOnScreen()
    #     val = dlg.ShowModal()

    #     if val == wx.ID_OK:
    #         for i, txtlist in enumerate(dlg.txtlists):
    #             ds = [txt.GetLineText(0) for txt in txtlist]
    #             model.add_descriptions(name, ds, i+1)

    #     dlg.Destroy()

    def onChangeReg(self, event):
        selected = self.GetFirstSelected()
        name = self.GetItem(selected, 0).GetText()
        model = self.fmf.model

        dlg = RegistersDialog(self, wx.ID_ANY, name, model,
                              title='Source Registers')

        dlg.CenterOnScreen()
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            treg = dlg.chTemp.GetString(dlg.chTemp.GetSelection())
            tch = int(dlg.chTchannel.GetString(dlg.chTchannel.GetSelection()))
            s1reg = dlg.chSide1.GetString(dlg.chSide1.GetSelection())
            s2reg = dlg.chSide2.GetString(dlg.chSide2.GetSelection())

            model.change_sources(name, treg=treg, tch=tch,
                                 s1reg=s1reg, s2reg=s2reg)
            df = model[name]
            HKEConfig.add_loaded_file(df)

        dlg.Destroy()

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


class ChannelsDialog(wx.Dialog):
    def __init__(self, parent, id, dataname, model, **kwargs):
        wx.Dialog.__init__(self, parent, id,
                           style=(wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER),
                           **kwargs)

        self.model = model
        self.dataname = dataname
        self.dewar = self.model[dataname]['dewar']
        self.txtlists = []

        self.bsMain = wx.BoxSizer(wx.VERTICAL)

        self.lblTitle = wx.StaticText(self, wx.ID_ANY,
            "Showing channels for: {dfname}".format(dfname=dataname))

        self.bsMain.Add(self.lblTitle, 0, wx.EXPAND)
        self.bsMain.Add(wx.StaticLine(self, wx.ID_ANY), 0, wx.EXPAND)
        self.bsMain.Add((5, 5))

        # Make the Channel lists
        self.bsLists = wx.BoxSizer(wx.HORIZONTAL)

        self.bsChList1, txtList = self.make_channel_list(1)
        self.txtlists.append(txtList)
        self.bsLists.Add(self.bsChList1, 1, wx.EXPAND)

        if self.dewar == 'shiny':
            # Vertical line for spacing - Doesn't seem to work
            self.bsLists.Add((10, 5))
            self.bsLists.Add(wx.StaticLine(self, wx.ID_ANY,
                                           style=wx.LI_VERTICAL),
                             0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
            self.bsLists.Add((10, 5))

            # Add second column of channels
            self.bsChList2, txtList2 = self.make_channel_list(2)
            self.txtlists.append(txtList2)
            self.bsLists.Add(self.bsChList2, 1, wx.EXPAND)

        self.bsMain.Add(self.bsLists, 1, wx.EXPAND)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        self.bsMain.Add(btnsizer, 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(self.bsMain)
        self.bsMain.Fit(self)
        self.Show()

    def make_channel_list(self, side=1):
        model = self.model
        ds = model[self.dataname][
            'Side {s} Descriptions'.format(s=side)]

        bsChList = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, wx.ID_ANY,
                            'Side {s}'.format(s=side))
        bsChList.Add(lbl, 0, wx.ALL | wx.CENTER)
        txtList = []

        for i, d in enumerate(ds):
            lbl = wx.StaticText(self, wx.ID_ANY,
                                'Channel {i:2}'.format(i=i))
            txt = wx.TextCtrl(self, wx.ID_ANY, d)

            txtList.append(txt)

            bs = wx.BoxSizer(wx.HORIZONTAL)
            bs.Add(lbl, 0, wx.EXPAND | wx.RIGHT)
            bs.Add(txt, 1, wx.EXPAND | wx.LEFT)

            bsChList.Add(bs, 0, wx.EXPAND)

        return bsChList, txtList


class RegistersDialog(wx.Dialog):
    def __init__(self, parent, id, dataname, model, **kwargs):
        wx.Dialog.__init__(self, parent, id,
                           style=(wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER),
                           **kwargs)

        self.model = model
        self.dataname = dataname
        self.dewar = self.model[dataname]['dewar']
        self.f = self.model[self.dataname]['file']
        self.registers = self.f.list_registers()

        self.bsMain = wx.BoxSizer(wx.VERTICAL)

        self.lblTitle = wx.StaticText(self, wx.ID_ANY,
                                      "Select source registers for:"
                                      " {dfname}".format(dfname=dataname))

        self.bsMain.Add(self.lblTitle, 0, wx.EXPAND)
        self.bsMain.Add(wx.StaticLine(self, wx.ID_ANY), 0, wx.EXPAND)
        self.bsMain.Add((5, 5))

        self.bsTemp, self.chTemp = self.make_dropdown('Temperature')
        self.bsSide1, self.chSide1 = self.make_dropdown('Side 1')
        if self.dewar == 'craac':
            tdefault = self.registers.index('ADR Root coil (1-DSPID):'
                                            ' Demod')
            s1default = self.registers.index('4W Quadrant'
                                             ' (4-TRead_LR): Demod')
            self.chTemp.SetSelection(tdefault)
            self.chSide1.SetSelection(s1default)
        elif self.dewar == 'shiny':
            self.bsSide2, self.chSide2 = self.make_dropdown('Side 2')

            try:
                tdefault = self.registers.index(
                    'SHINY_T4 (5-TRead_Standard): Demod')
            except ValueError:
                tdefault = 0
            try:
                s1default = self.registers.index(
                    'SHINY_T3 (8-TRead_LR): Demod')
            except ValueError:
                s1default = 0
            try:
                s2default = self.registers.index(
                    'SHINY_T1 (4-TRead_LR): Demod')
            except ValueError:
                s2default = 0
            self.chTemp.SetSelection(tdefault)
            self.chSide1.SetSelection(s1default)
            self.chSide2.SetSelection(s2default)

        self.bsTchannel = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(self, wx.ID_ANY, 'Temp Channel')
        self.chTchannel = wx.Choice(self, wx.ID_ANY, choices=['0'])
        self.update_tchannel()
        self.bsTchannel.Add(lbl, 0, wx.EXPAND)
        self.bsTchannel.Add(self.chTchannel, 1, wx.EXPAND)

        self.bsMain.Add(self.bsTemp, 1, wx.EXPAND)
        self.bsMain.Add(self.bsTchannel, 1, wx.EXPAND)
        self.bsMain.Add((20, 20))
        self.bsMain.Add(self.bsSide1, 1, wx.EXPAND)
        if self.dewar == 'shiny':
            self.bsMain.Add((20, 20))
            self.bsMain.Add(self.bsSide2, 1, wx.EXPAND)

        self.Bind(wx.EVT_CHOICE, self.onChoice, self.chTemp)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        self.bsMain.Add(btnsizer, 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(self.bsMain)
        self.bsMain.Fit(self)
        self.Show()

    def make_dropdown(self, label):
        lbl = wx.StaticText(self, wx.ID_ANY, label)
        ch = wx.Choice(self, wx.ID_ANY, choices=self.registers)

        bs = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(lbl, 0, wx.EXPAND)
        bs.Add(ch, 1, wx.EXPAND)

        return bs, ch

    def update_tchannel(self):
        oldsel = self.chTchannel.GetSelection()
        tsel = self.chTemp.GetSelection()
        data = self.f.get_data(tsel)
        nch = data.shape[-1]
        newchoices = [str(i) for i in range(nch)]

        self.chTchannel.Clear()
        for choice in newchoices:
            self.chTchannel.Append(choice)

        if oldsel < nch:
            self.chTchannel.SetSelection(oldsel)

    def onChoice(self, event):
        self.update_tchannel()
