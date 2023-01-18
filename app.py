import wx 
import sqlite3

class OurPopupMenu(wx.Menu):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.Append(wx.MenuItem(self, wx.ID_NEW, '增加同级'))
        self.Append(wx.MenuItem(self, wx.ID_ADD, '增加下级'))
        self.Append(wx.MenuItem(self, wx.ID_DELETE, '删除此项'))


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title)
        self.SetSize((700, 300))
        self.textCtrls = [] # 右侧信息列表
        #self.itemData = []  # 被选中项目的值
        self.colNames = ['编号', '姓名', '手机号', '上级编号', '个人业绩']
        
        self.panel = wx.Panel(self)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.functionBox = wx.BoxSizer(wx.HORIZONTAL)
        self.totalBox = wx.BoxSizer(wx.VERTICAL)
        self.totalBox.Add(self.box, flag=wx.EXPAND)
        self.totalBox.Add(self.functionBox)
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
        self.Bind(wx.EVT_BUTTON, self.btnHandler)
        # TODO:
        #self.Bind(wx.EVT_MENU, self.menuHandler, self.popupMenu)

        self.Centre()
    
    def treeSelChanged(self, e):
        treeItem = e.GetItem() 
        treeData = self.tree.GetItemData(treeItem)

        if not self.tree.GetItemParent(treeItem).IsOk():    
            return 
        else:
            for i in range(len(treeData) - 1):
                self.textCtrls[i].SetValue(str(treeData[i+1]))
            self.textCtrls[-1].SetValue(str(self.getItemTotalValue(treeItem)))
    
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
        pass 

    def menuHandler(self, e):
        # handler不能传参数，要知道处理的是哪个item必须记录在class的属性里！ TODO:
        # 这些修改都应该是直接对数据库做的，修改后再更新treeView即可
        eid = e.GetId()
        if eid == wx.ID_DELETE:
            self.DeleteItem() 
        else:
            pass 

    def DeleteItem():
        pass 

    def readTreeData(self):
        treeData = [
            (0, '所有数据', None, None, None),
            (1, 'Alice', '12345678', 0, 100),
            (2, 'Bob', '32132234', 1, 12),
            (3, 'Lily', 0, 1, 16),
            (4, 'Lucy', '33298726', 3, 30),
            (5, 'Bob', '12311245', None, 16)
        ]
        self.treeData = treeData

    def initTreeView(self):
        self.tree = wx.TreeCtrl(self.panel)
        #self.tree.SetQuickBestSize(False)
        rootItem = self.tree.AddRoot('所有数据', data=self.treeData[0])

        def makeTree(parent):
            parentItemData = self.tree.GetItemData(parent)
            parentId = parentItemData[0]
            childrenData = [_ for _ in self.treeData if _[3] == parentId]
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
    
    def updateTreeView(self):
        self.initTreeView()
        self.updateTreeLabel()

    def initDetailView(self):
        rightBox = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(5, 2)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        rightBox.Add(gbs, flag=wx.ALL, border=5)
        rightBox.Add(btnBox, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=20)
        self.box.Add(rightBox, flag=wx.ALL, border=10)
        
        for i, name in enumerate(self.colNames[1:]):
            gbs.Add(wx.StaticText(self.panel, label=name), (i, 0), flag=wx.ALIGN_CENTER_VERTICAL)
            # 不开启编辑，均为只读
            tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
            self.textCtrls.append(tc)
            gbs.Add(tc, (i, 1), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=8)   
        
        # 总个人业绩永远为只读     
        gbs.Add(wx.StaticText(self.panel, label='总个人业绩（自动计算）'), (5, 0))
        tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
        self.textCtrls.append(tc)
        gbs.Add(tc, (5, 1), flag=wx.LEFT, border=8)
        
        btnBox.Add(wx.Button(self.panel, wx.ID_EDIT, '编辑', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        btnBox.Add(wx.Button(self.panel, wx.ID_SAVE, '保存', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)

    def initFunctionView(self):
        pass


def main():
    app = wx.App()
    frm = MainFrame(None, title='树结构信息管理')
    frm.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()