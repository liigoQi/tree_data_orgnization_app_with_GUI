import wx 
import sqlite3
import datetime
from database import Database

class OurPopupMenu(wx.Menu):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.Append(wx.MenuItem(self, wx.ID_NEW, '增加同级'))
        self.Append(wx.MenuItem(self, wx.ID_ADD, '增加下级'))
        self.Append(wx.MenuItem(self, wx.ID_DELETE, '删除此项'))


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
        self.totalBox.Add(self.box, flag=wx.EXPAND)
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
        # TODO:
        #self.Bind(wx.EVT_MENU, self.menuHandler, self.popupMenu)

        self.Centre()
    
    def treeSelChanged(self, e):
        self.treeItem = e.GetItem() 
        treeData = self.tree.GetItemData(self.treeItem)

        if not self.tree.GetItemParent(self.treeItem).IsOk():    
            return 
        else:
            i = 0
            while i < len(treeData):
                if i < 2: 
                    self.textCtrls[i].SetValue(str(treeData[i+1]))
                elif i > 2:
                    self.textCtrls[i-1].SetValue(str(treeData[i]))
                i += 1
            #self.textCtrls[-1].SetValue(str(self.getItemTotalValue(self.treeItem)))
    
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
        pass
        #editableCtrls = self.textCtrls[]

    def saveData(self):
        pass 

    def deleteAllValues(self):
        pass 

    def menuHandler(self, e):
        # handler不能传参数，要知道处理的是哪个item必须记录在class的属性里！ TODO:
        # 这些修改都应该是直接对数据库做的，修改后再更新treeView即可
        eid = e.GetId()
        if eid == wx.ID_DELETE:
            self.DeleteItem() 
        else:
            pass 

    def DeleteItem(self):
        pass 

    def readTreeData(self):
        self.treeData = self.db.getData(self.table)
        #print(self.treeData)

    def initTreeView(self):
        self.tree = wx.TreeCtrl(self.panel)
        #self.tree.SetQuickBestSize(False)
        rootItem = self.tree.AddRoot('所有数据', data=self.treeData[0])

        def makeTree(parent):
            parentItemData = self.tree.GetItemData(parent)
            parentId = parentItemData[0]
            childrenData = [_ for _ in self.treeData if _[2] == parentId]
            if childrenData:
                for data in childrenData:
                    childItem = self.tree.AppendItem(parent, data[1], data=data)
                    makeTree(childItem)
                    #self.tree.Expand(childItem)
            else:
                return 
            
        makeTree(rootItem)
        leftBox = wx.BoxSizer()
        leftBox.Add(self.tree, 1, wx.EXPAND | wx.ALL, border=5)
        self.box.Add(leftBox, 1, wx.EXPAND | wx.ALL, border=10)
        self.tree.ExpandAllChildren(rootItem)

    def updateTreeLabel(self):  # 更新

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

    def updateTreeData(self):
        pass 
    
    def updateTreeView(self):
        self.initTreeView()
        self.updateTreeLabel()

    def initDetailView(self):
        self.rightBox = wx.StaticBoxSizer(wx.VERTICAL, self.panel, '详细信息')
        gbs = wx.GridBagSizer(5, 2)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.rightBox.Add(gbs, flag=wx.ALL, border=5)
        self.rightBox.Add(btnBox, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=20)
        self.box.Add(self.rightBox, flag=wx.ALL, border=15)
        
        for i, name in enumerate(self.colNames):
            if i == 2:
                continue 
            elif i < 2:
                gbs.Add(wx.StaticText(self.panel, label=name), (i, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                # 不开启编辑，均为只读
                tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
                self.textCtrls.append(tc)
                gbs.Add(tc, (i, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)   
            else:
                gbs.Add(wx.StaticText(self.panel, label=name), (i-1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                # 不开启编辑，均为只读
                tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
                self.textCtrls.append(tc)
                gbs.Add(tc, (i-1, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)  
        
        # 总个人业绩永远为只读     
        gbs.Add(wx.StaticText(self.panel, label='总个人业绩（自动计算）'), (4, 0))
        tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
        self.textCtrls.append(tc)
        gbs.Add(tc, (4, 1), flag=wx.LEFT, border=8)
        
        btnBox.Add(wx.Button(self.panel, wx.ID_EDIT, '编辑', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        btnBox.Add(wx.Button(self.panel, wx.ID_SAVE, '保存', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        print(len(self.textCtrls))

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