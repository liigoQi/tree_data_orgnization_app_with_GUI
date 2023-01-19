import sqlite3
import datetime 

class Database(object):
    def __init__(self) -> None:
        self.conn = sqlite3.connect('MyData.db')
        self.cur = self.conn.cursor()

    def createTable(self, table, ifDrop=False):
        if ifDrop:
            self.cur.execute(f'drop table {table};')
        sql = f"""create table {table} (
            会员号 varchar(20) primary key not null,
            姓名 varchar(20) not null,
            上级会员号 varchar(20),
            注册日期 date,
            个人业绩 int default 0);
            """
        self.cur.execute(sql)
        self.conn.commit()
        return True 

    def initDB(self, table, ifTest=False):
        if not ifTest:
            self.createTable(table, ifDrop=True)
            self.insertRows(table, rows=(('0', '所有数据', 'NULL', 'NULL', 'NULL')))
        else:
            self.createTable(table, ifDrop=True)
            self.insertTestData(table)

    def insertTestData(self, table):
        # ['会员号', '姓名', '上级会员号', '注册日期', '个人业绩']
        rows = [
            ('0', '所有数据', 'NULL', 'NULL', 'NULL'),
            ('00140830', '樊晓兰', '0', '2017-01-01', 100),
            ('001408301', '小红', '00140830', '2017-03-08', 12),
            ('00140832', '小蓝', '00140830', '2018-04-03', 16),
            ('00140834', '小绿', '00140831', '2020-09-05', 30),
            ('00140835', '小紫', '00140831', '2022-03-07', 16)
        ]
        self.cur.execute(f'delete from {table};')
        self.conn.commit()
        return self.insertRows(table, rows)

    def getData(self, table, condition=None):
        if condition:
            sql = f'select * from {table} where {condition};'
        else:
            sql = f'select * from {table};'
        self.cur.execute(sql)   # 执行
        return self.cur.fetchall()  # 取回

    def getColNames(self, table):
        self.cur.execute(f'select * from {table};')
        names = [_[0] for _ in self.cur.description]
        return names 

    def insertRows(self, table, rows):
        rowsStr = str(rows)[1:-1]
        sql = f'insert into {table} values {rowsStr};'
        self.cur.execute(sql)
        self.conn.commit()
        return True 

    def updateRows(self, table, content, condition):
        key = ''
        value = []
        for k, v in content.items():
            key += f'{k}=?,'
            value.append(v)
        key = key[:-1]
        sql = f'update {table} set {key} where {condition};'
        self.cur.execute(sql, value)
        self.conn.commit()
        return True 
        #data = self.getData(table)

    def deleteRows(self, table, condition):
        sql = f'delete from {table} where {condition};'
        self.cur.execute(sql)
        self.conn.commit()
        return True 