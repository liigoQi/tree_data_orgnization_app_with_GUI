import wx 
import sqlite3

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title)
        self.SetSize((500, 300))
        self.textCtrls = [] # 右侧信息列表
        #self.itemData = []  # 被选中项目的值
        self.colNames = ['编号', '姓名', '手机号', '上级编号', '个人业绩']
        
        self.panel = wx.Panel(self)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(self.box)

        self.readTreeData()
        self.initTreeView()
        self.initDetailView()

        self.infoBox = wx.BoxSizer(wx.VERTICAL)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.treeSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.treeRightClick, self.tree)
        self.Bind(wx.EVT_BUTTON, self.btnHandler)

        self.Centre()
    
    def treeSelChanged(self, e):
        treeItem = e.GetItem() 
        treeData = self.tree.GetItemData(treeItem)

        if not treeData:    # 点击root时treeData为0
            return 
        else:
            for i in range(len(treeData) - 1):
                self.textCtrls[i].SetValue(str(treeData[i+1]))
            self.textCtrls[-1].SetValue(str(self.getItemTotalValue(treeItem)))
    
    def getItemTotalValue(self, treeItem):
        treeData = self.tree.GetItemData(treeItem)
        return 1

    def treeRightClick(self, e):
        pass 

    def btnHandler(self, e):
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
        rootItem = self.tree.AddRoot('所有数据', data=self.treeData[0])

        def makeTree(parent):
            parentItemData = self.tree.GetItemData(parent)
            parentId = parentItemData[0]
            childrenData = [_ for _ in self.treeData if _[3] == parentId]
            if childrenData:
                for data in childrenData:
                    childItem = self.tree.AppendItem(parent, data[1], data=data)
                    makeTree(childItem)
            else:
                return 
            
        makeTree(rootItem)
        leftBox = wx.BoxSizer()
        leftBox.Add(self.tree, 1, wx.EXPAND)
        self.box.Add(leftBox, 1, wx.EXPAND | wx.ALL, border=10)
        self.tree.Expand(rootItem)

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
            gbs.Add(tc, (i, 1), flag=wx.LEFT, border=8)   
        
        # 总个人业绩永远为只读     
        gbs.Add(wx.StaticText(self.panel, label='总个人业绩'), (5, 0))
        tc = wx.TextCtrl(self.panel, size=(150, -1), style=wx.TE_READONLY)
        self.textCtrls.append(tc)
        gbs.Add(tc, (5, 1), flag=wx.LEFT, border=8)
        
        btnBox.Add(wx.Button(self.panel, wx.ID_EDIT, '编辑', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)
        btnBox.Add(wx.Button(self.panel, wx.ID_SAVE, '保存', size=(60, 30)), flag=wx.LEFT | wx.RIGHT, border=10)

def main():
    app = wx.App()
    frm = MainFrame(None, title='树结构信息管理')
    frm.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()