import wx 
import wx.adv
import sqlite3
import datetime
from database import Database

class OurPopupMenu(wx.Menu):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.Append(wx.MenuItem(self, wx.ID_NEW, '增加同级'))
        self.Append(wx.MenuItem(self, wx.ID_ADD, '增加下级'))
        self.Append(wx.MenuItem(self, wx.ID_DELETE, '删除此项'))

class InputDialog(wx.Dialog):
    def __init__(self, parent, inputColNames):
        super().__init__(parent, wx.ID_ANY, '新增项目', size=(300, 260))
        self.data = None 

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.inputColNames = inputColNames
        self.tcs = []
        
        self.box = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(5, 2)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(gbs, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, border=15)
        self.box.Add(btnBox, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=10)
        
        for i, name in enumerate(self.inputColNames):
            if name in ['会员号', '姓名']:
                tmp_name = name + '*'
            else:
                tmp_name = name
            gbs.Add(wx.StaticText(self.panel, label=tmp_name), (i, 0), flag=wx.ALIGN_CENTER_VERTICAL)
            if i == 3:
                tc = wx.adv.DatePickerCtrl(self.panel, size=(150, -1))
            else:
                tc = wx.TextCtrl(self.panel, size=(150, -1))
            gbs.Add(tc, (i, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)    
            self.tcs.append(tc)

        self.saveBtn = wx.Button(self.panel, wx.ID_SAVE, label='保存')
        self.cancelBtn = wx.Button(self.panel, wx.ID_CANCEL, label='取消')
        btnBox.Add(self.saveBtn, flag=wx.RIGHT | wx.TOP, border=10)
        btnBox.Add(self.cancelBtn, flag=wx.LEFT | wx.TOP, border=10)

        self.saveBtn.Bind(wx.EVT_BUTTON, self.popData)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.cancel)
        self.Bind(wx.EVT_CLOSE, self.cancel)

        self.tcs[-1].SetValue('0')

        self.panel.SetSizer(self.box)
        self.CentreOnParent()
        self.Show()

    def popData(self, e):
        #content = {self.inputColNames[i]: self.tcs[i].GetValue() for i in range(len(self.inputColNames))}
        #content['个人业绩'] = int(content['个人业绩'])
        data = [self.tcs[i].GetValue() for i in range(len(self.tcs))]
        data[-1] = int(data[-1])
        # wx.DateTime转为字符串
        data[3] = data[3].Format('%y-%m-%d')
        self.data = data 
        self.EndModal(wx.ID_SAVE)
        self.Destroy()
        return wx.ID_OK

    def cancel(self, e):
        self.data = None 
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()
        return wx.ID_CANCEL

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title)
        self.SetSize((700, 400))
        self.textCtrls = [] # 右侧信息列表
        self.treeItem = None    # 被选中的item
        
        self.table = 'sample_db'
        self.db = Database()
        self.db.initDB(self.table, ifTest=True)
        # 上级会员号不用显示，通过popmenu添加数据时自动设置
        # self.colNames = ['会员号', '姓名', '上级会员号', '注册日期', '个人业绩']
        self.colNames = self.db.getColNames(self.table)
        self.keyName = self.colNames[0]
        
        self.panel = wx.Panel(self)
        
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.functionBox = wx.BoxSizer(wx.HORIZONTAL)
        self.totalBox = wx.BoxSizer(wx.VERTICAL)
        self.totalBox.Add(self.box, flag=wx.ALL | wx.EXPAND, border=5)
        self.totalBox.Add(self.functionBox, flag=wx.ALIGN_CENTER_HORIZONTAL)
        self.panel.SetSizer(self.totalBox)

        self.popupMenu = OurPopupMenu()

        self.readTreeData()
        self.initTreeView()
        self.updateTreeLabel()  # 创建好树后将label更新为 姓名（个人业绩/个人总业绩）
        self.initDetailView()
        self.initFunctionView()

        self.infoBox = wx.BoxSizer(wx.VERTICAL)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.treeSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.treeRightClick, self.tree)
        # btnHandler处理所有button的事件
        self.Bind(wx.EVT_BUTTON, self.btnHandler)
        # menuHandler处理所有menu的事件
        self.Bind(wx.EVT_MENU, self.menuHandler)

        self.Centre()
    
    def updateDetailView(self):
        treeData = self.tree.GetItemData(self.treeItem)
        for i in range(len(treeData)):
            self.textCtrls[i].SetValue(str(treeData[i]))
        self.textCtrls[-1].SetValue(str(self.getItemTotalValue(self.treeItem)))

    # 根据self.tree上item的data决定右侧显示的内容
    def treeSelChanged(self, e):
        self.treeItem = e.GetItem() 
        if not self.tree.GetItemParent(self.treeItem).IsOk():    
            for tc in self.textCtrls:
                tc.SetValue('')
        else:
            self.updateDetailView()
    
    def getItemTotalValue(self, treeItem):
        treeData = self.tree.GetItemData(treeItem)
        selfValue = treeData[-1]
        totalValue = selfValue
        if self.tree.ItemHasChildren(treeItem):
            childItem, cookie = self.tree.GetFirstChild(treeItem)
            while childItem.IsOk():
                totalValue += self.getItemTotalValue(childItem)
                childItem, cookie = self.tree.GetNextChild(treeItem, cookie)
            return totalValue
        else:
            return totalValue

    def treeRightClick(self, e):
        item = e.GetItem()
        itemData = self.tree.GetItemData(item)
        self.tree.SelectItem(item)
        self.panel.PopupMenu(self.popupMenu)

    def btnHandler(self, e):
        button = e.GetEventObject()
        label = button.GetLabel()
        if label == '展开全部':
            rootItem = self.tree.GetRootItem()
            self.tree.ExpandAllChildren(rootItem)
        elif label == '收起全部':
            rootItem = self.tree.GetRootItem()
            self.tree.CollapseAllChildren(rootItem)
        elif label == '清空业绩':
            self.deleteAllValues()
        elif label == '突出显示':
            pass 
        elif label == '保存':
            self.saveData()
        elif label == '编辑':
            self.enableEdit()

    def enableEdit(self):
        editableCtrls = self.textCtrls[:-1]
        for tc in editableCtrls:
            tc.SetEditable(True)
        self.gbs.Detach(self.textCtrls[3])
        self.textCtrls[3].Hide()
        self.gbs.Add(self.datePicker, (3, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)
        data = self.tree.GetItemData(self.treeItem)
        date = wx.DateTime()
        date.ParseFormat(data[3], '%Y-%m-%d')
        #print(date)
        self.datePicker.SetValue(date)
        self.datePicker.Show()
        self.gbs.Layout()

    def saveData(self):
        oldData = self.tree.GetItemData(self.treeItem)
        newData = [_.GetValue() for _ in self.textCtrls[:-1]]
        newData[-1] = int(newData[-1])
        newData[3] = self.datePicker.GetValue().Format('%Y-%m-%d')
        #print(newData[3])
        content = dict()
        for i in range(len(newData)):
            content[self.colNames[i]] = newData[i]
        condition = f'{self.keyName}=\'{oldData[0]}\''
        if self.db.updateRows(self.table, content, condition):
            wx.MessageBox('数据更新成功！')
            # 如果修改了上级会员号则需要重新加载数据、重新生成树
            if newData[2] != oldData[2]:
                self.readTreeData()
                self.reloadTreeView() 
            else:
                # 如果修改本身的会员号需要将它的孩子的上级会员号全修改
                if newData[0] != oldData[0]:
                    # 将上级会员号=oldData[0]的行的上级会员号都改成newData[0]
                    tmp_content = {'上级会员号': newData[0]}
                    tmp_condition = f'上级会员号=\'{oldData[0]}\''
                    self.db.updateRows(self.table, tmp_content, tmp_condition)
                    self.readTreeData()
                    self.reloadTreeView()
                # 否则只需要更新当前item的data然后更新label即可
                else:
                    self.tree.SetItemData(self.treeItem, data=newData)
                    self.updateDetailView()
                    self.updateTreeLabel()
            
            self.gbs.Detach(self.datePicker)
            self.datePicker.Hide()
            self.gbs.Add(self.textCtrls[3], (3, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)
            self.textCtrls[3].Show()
            self.gbs.Layout()

    def deleteAllValues(self):
        content = {'个人业绩': 0}
        self.db.updateRows(self.table, content)
        self.readTreeData()
        self.reloadTreeView()

    def menuHandler(self, e):
        # handler不能传参数，要知道处理的是哪个item必须记录在class的属性里！
        # 这些修改都应该是直接对数据库做的，修改后再更新treeView即可
        eid = e.GetId()
        if eid == wx.ID_DELETE:
            self.deleteItem() 
        elif eid == wx.ID_ADD:  # 增加下级
            self.addChildItem()
        elif eid == wx.ID_NEW:  # 增加同级
            self.addSiblingItem()

    def deleteItem(self):
        dialog = wx.MessageDialog(self.panel, '将删除该项目及其所有子项目，是否确定？', '警告',wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION) 
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            data = self.tree.GetItemData(self.treeItem)
            key = data[0]
            # 删除自己
            cond1 = f'会员号=\'{key}\''
            self.db.deleteRows(self.table, cond1)
            # 删除它的孩子
            cond2 = f'上级会员号=\'{key}\''
            self.readTreeData()
            self.reloadTreeView()

    def addChildItem(self):
        curData = self.tree.GetItemData(self.treeItem)
        key = curData[0]
        dialog = InputDialog(self.panel, self.colNames)
        # 自动填充上级会员号
        dialog.tcs[2].SetValue(key)
        dialog.tcs[2].SetEditable(False)
        dialog.tcs[3].SetValue(wx.DateTime.Today())
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            newData = dialog.data
            rows = [tuple(newData)]
            self.db.insertRows(self.table, rows)
            self.readTreeData()
            self.reloadTreeView()
            self.selectItemWithKey(newData[0])
        
    def addSiblingItem(self):
        curData = self.tree.GetItemData(self.treeItem)
        parent = curData[2]
        dialog = InputDialog(self.panel, self.colNames)
        # 自动填充上级会员号
        dialog.tcs[2].SetValue(parent)
        dialog.tcs[2].SetEditable(False)
        dialog.tcs[3].SetValue(wx.DateTime.Today())
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            newData = dialog.data
            rows = [tuple(newData)]
            self.db.insertRows(self.table, rows)
            self.readTreeData()
            self.reloadTreeView()
            self.selectItemWithKey(newData[0])

    def readTreeData(self):
        self.treeData = self.db.getData(self.table)

    # 从self.treeData创建树
    def makeTree(self, parent):
        parentItemData = self.tree.GetItemData(parent)
        parentId = parentItemData[0]
        childrenData = [_ for _ in self.treeData if _[2] == parentId]
        if childrenData:
            for data in childrenData:
                childItem = self.tree.AppendItem(parent, data[1], data=data)
                self.makeTree(childItem)
                #self.tree.Expand(childItem)
        else:
            return 
    
    def initTreeView(self):
        self.tree = wx.TreeCtrl(self.panel, style=wx.VSCROLL | wx.HSCROLL)
        #self.tree.SetQuickBestSize(False)
        rootItem = self.tree.AddRoot('所有数据', data=self.treeData[0])
        self.makeTree(rootItem)
        leftBox = wx.BoxSizer()
        leftBox.Add(self.tree, 1, wx.EXPAND | wx.ALL, border=5)
        self.box.Add(leftBox, 1, wx.EXPAND | wx.ALL, border=10)
        self.tree.ExpandAllChildren(rootItem)

    def updateTreeLabel(self):  # 更新
        # 在已经有一颗树且每个节点有正确的data后调用

        def updateSubtreeLabel(item):  # 更新一个节点和其子树的标签
            itemData = self.tree.GetItemData(item)
            name, value = itemData[1], itemData[-1]
            totalValue = self.getItemTotalValue(item)
            self.tree.SetItemText(item, f'{name}（{value}/{totalValue}）')
            if self.tree.ItemHasChildren(item):
                childItem, cookie = self.tree.GetFirstChild(item)
                while childItem.IsOk():
                    updateSubtreeLabel(childItem)
                    childItem, cookie = self.tree.GetNextChild(childItem, cookie)
            else:
                return 

        rootItem = self.tree.GetRootItem()

        if self.tree.ItemHasChildren(rootItem):
            childItem, cookie = self.tree.GetFirstChild(rootItem)
            while childItem.IsOk():
                updateSubtreeLabel(childItem)
                childItem, cookie = self.tree.GetNextChild(childItem, cookie)

    def selectItemWithKey(self, key):
        
        def findItemWithKey(parent, key):
            parentItemData = self.tree.GetItemData(parent)
            parentId = parentItemData[0]
            if parentId == key:
                return parent
            else:
                if self.tree.ItemHasChildren(parent):
                    childItem, cookie = self.tree.GetFirstChild(parent)
                    while childItem.IsOk():
                        item = findItemWithKey(childItem, key)
                        if item != None:
                            return item 
                        childItem, cookie = self.tree.GetNextChild(parent, cookie)
            return None 
        
        item = findItemWithKey(self.tree.RootItem, key)
        if item:
            self.treeItem = item 
            self.tree.SelectItem(item)

    def reloadTreeView(self):
        self.tree.DeleteAllItems()  # 清空树
        rootItem = self.tree.AddRoot('所有数据', data=self.treeData[0])    
        self.makeTree(rootItem)
        self.tree.ExpandAllChildren(rootItem)
        self.updateTreeLabel()
        self.tree.SelectItem(rootItem)

    def initDetailView(self):
        self.rightBox = wx.StaticBoxSizer(wx.VERTICAL, self.panel, '详细信息')
        self.gbs = wx.GridBagSizer(5, 2)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.rightBox.Add(self.gbs, flag=wx.ALL | wx.EXPAND, border=5)
        self.rightBox.Add(btnBox, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=20)
        self.box.Add(self.rightBox, flag=wx.ALL | wx.EXPAND, border=15)
        
        for i, name in enumerate(self.colNames):
            self.gbs.Add(wx.StaticText(self.panel, label=name), (i, 0), flag=wx.ALIGN_CENTER_VERTICAL)
            # 不开启编辑，均为只读
            tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
            self.textCtrls.append(tc)
            self.gbs.Add(tc, (i, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)    
        
        # 总个人业绩永远为只读     
        self.gbs.Add(wx.StaticText(self.panel, label='总个人业绩（自动计算）'), (len(self.colNames), 0))
        tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
        self.textCtrls.append(tc)
        self.gbs.Add(tc, (len(self.colNames), 1), flag=wx.LEFT, border=8)
        
        self.datePicker = wx.adv.DatePickerCtrl(self.panel, size=(150, -1))
        self.datePicker.Hide()
        
        btnBox.Add(wx.Button(self.panel, wx.ID_EDIT, '编辑', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        btnBox.Add(wx.Button(self.panel, wx.ID_SAVE, '保存', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        #(len(self.textCtrls))

    def initFunctionView(self):
        self.functionBox.Add(wx.Button(self.panel, wx.ID_ANY, '展开全部', size=(80, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        self.functionBox.Add(wx.Button(self.panel, wx.ID_ANY, '收起全部', size=(80, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        self.functionBox.Add(wx.Button(self.panel, wx.ID_ANY, '清空业绩', size=(80, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        self.functionBox.Add(wx.Button(self.panel, wx.ID_ANY, '突出显示', size=(80, 30)), flag=wx.LEFT | wx.RIGHT, border=10)

def main():
    app = wx.App()
    frm = MainFrame(None, title='树结构信息管理')
    frm.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()