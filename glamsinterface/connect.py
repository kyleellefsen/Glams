# encoding: utf-8
import mysql.connector
import codecs
import os.path
import glamsinterface


def importconfig():
    '''this function loads the config.txt file into a dictionary which is used by the 'connect.py' module.
    config.txt is a file which includes database connection information'''
    config=dict()
    filename=os.path.join(os.path.dirname(glamsinterface.__file__),'config.txt')
    BOM = codecs.BOM_UTF8.decode('utf8')
    with codecs.open(filename, encoding='utf-8') as f:
        for line in f:
            line = line.lstrip(BOM)
            line=line.split('=')
            config[line[0].lstrip().rstrip()]=line[1].lstrip().rstrip()
    return config
        
class DB:
    cnx=None
    def __init__(self):
        self.config=importconfig()
    def connect(self):
        self.cnx=mysql.connector.connect(host=str(self.config['mysql_IP_address']), 
                                         user=str(self.config['user']), 
                                         database=str(self.config['database']), 
                                         password=str(self.config['password']), 
                                         port=int(self.config['port']))

        return self.cnx.cursor(buffered=True)
    def execute(self,command, entriesTuple=None, commit=True):
        cursor=self.connect()
        cursor.execute(command,entriesTuple)
        #except mysql.connector.errors.ProgrammingError as e:
         #   self.cnx.close()
         #   print(e.msg)
         #   return e
        try:
            data=cursor.fetchall()
        except mysql.connector.errors.InterfaceError:
            data=tuple()
        cursor.close()
        if commit:
            self.cnx.commit()
        return data
        self.cnx.close()
db=DB()

class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None
        
class DB2:
    cnx=None
    def __init__(self):
        self.config=importconfig()
    def connect(self):
        self.cnx=mysql.connector.connect(host=str(self.config['mysql_IP_address']), 
                                         user=str(self.config['user']), 
                                         database=str(self.config['database']), 
                                         password=str(self.config['password']), 
                                         port=int(self.config['port']))
        return self.cnx.cursor(buffered=True, cursor_class=MySQLCursorDict)
    def execute(self,command, entriesTuple=None, commit=True):
        cursor=self.connect()
        cursor.execute(command,entriesTuple)
        #except mysql.connector.errors.ProgrammingError as e:
         #   self.cnx.close()
         #   print(e.msg)
         #   return e
        try:
            data=cursor.fetchall()
        except mysql.connector.errors.InterfaceError:
            data=tuple()
        cursor.close()
        if commit:
            self.cnx.commit()
        return data
        self.cnx.close()
db2=DB2()