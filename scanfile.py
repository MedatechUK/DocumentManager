import os
import uuid
from pathlib import Path
from datetime import *

import pyodbc 
import json

import cv2 
from pyzbar.pyzbar import decode 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize

PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]

class PDFfile:
    def __init__(self, f , p , preauth):        
        self.uid = str(uuid.uuid4())
        self.folder = "f://scans//"        
        self.path = os.path.join(self.folder , self.uid + ".pdf")
        self.device = f.device
        self.thisuser = f.thisuser
        self.thisdate = f.thisdate
        self.barcode = p.barcode
        self.preauth = preauth
        self.url = "../../system/mail/scans/{}".format(self.uid + ".pdf")
        self.qrdata = p.inbuff
        self.hasqr = len(p.inbuff) > 0
        
    def constr(self):
        SERVER = 'CE-AZ-UK-S-PRIO'
        INSTANCE = 'TST'
        DATABASE = 'fuld1'
        USERNAME = 'tabula'
        PASSWORD = 'cheese8!'
        # dr = pyodbc.drivers()
        return (f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER}\\{INSTANCE};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};MARS_Connection=Yes')
    
    def dbSave(self):
        cnxn = pyodbc.connect(self.constr())
        cursor = cnxn.cursor() 
        for b in self.barcode:
            print(b.data.decode())
            iv = cursor.execute("SELECT        " 
                + "dbo.DOCUMENTS.DOC, ISNULL(1 + MAX(dbo.EXTFILES.EXTFILENUM), 1) " 
                + "FROM            dbo.DOCUMENTS LEFT OUTER JOIN dbo.EXTFILES ON dbo.DOCUMENTS.DOC = dbo.EXTFILES.IV "
                + "GROUP BY dbo.DOCUMENTS.DOC, dbo.DOCUMENTS.DOCNO, dbo.EXTFILES.TYPE "
                + "HAVING (dbo.DOCUMENTS.DOC > 0) "            
                + "AND    (dbo.EXTFILES.TYPE = N'D' OR dbo.EXTFILES.TYPE IS NULL)  "
                + "AND    (dbo.DOCUMENTS.DOCNO = N'{}') ".format(b.data.decode())
            )            
            for row in iv:  
                cursor2 = cnxn.cursor() 
                sql = ( "INSERT INTO EXTFILES ( IV " 
                    + ",      TYPE "
                    + ",      ZCLA_FILECATEGORY "
                    + ",      EXTFILENUM "
                    + ",      EXTFILENAME "
                    + ",      EXTFILEDES "
                    + ",      GUID "
                    + ",      CURDATE ) "
                    + "VALUES ( {} "
                    + ",       '{}' "          
                    + ",        {}  "
                    + ",        {}  "
                    + ",       '{}' "
                    + ",       '{}' "
                    + ",       '{}' "
                    + ",        {} )"                    
                ).format( row[0] 
                    , 'D' 
                    , -1
                    , row[1] 
                    , self.url 
                    , 'From ' + self.device
                    , self.uid 
                    , (datetime.date.today() - datetime.date(1988, 1, 1)).total_seconds() / 60 
                )                     
                # print(sql)                  
                ret = cursor2.execute( sql )                
                cursor2.close()

        cursor.close()
        cnxn.commit()
        cnxn.close()

    def dbSavePayCard(self):
        cnxn = pyodbc.connect(self.constr())
        cursor = cnxn.cursor() 
        sql = ("SELECT PROJACTSCHED "
            + "FROM ZCLA_PROJACTSCH "
            + "WHERE 0=0 "
            + "AND   PROJACT = {} "            
            + "AND   CONTRACTSCHED IN ( "
            + "SELECT CONTRACTSCHED "
            + "FROM ZCLA_CONTRACTSCHEDUL "
            + "WHERE IVDATE > datediff(minute,'1/1/1988', getdate()) "
            + ")"
        ).format( self.qrField("PROJACT") )   
        sched = cursor.execute(sql)

        for row in sched:  
            cursor2 = cnxn.cursor() 
            sql = ("SELECT      dbo.ZCLA_PROJACTSCH.PROJACTSCHED, dbo.nEXTFILENUM('{}', {}) "
                + "FROM         dbo.ZCLA_PROJACTSCH "                                
                + "WHERE        dbo.ZCLA_PROJACTSCH.PROJACTSCHED = {} "                
            ).format( '~'
                     , row[0] 
                     , row[0] 
            )
            iv = cursor2.execute(sql)
            
            for row2 in iv:                  
                cursor3 = cnxn.cursor() 
                sql = ( "INSERT INTO EXTFILES ( IV " 
                    + ",      TYPE "
                    + ",      ZCLA_FILECATEGORY "
                    + ",      EXTFILENUM "
                    + ",      EXTFILENAME "
                    + ",      EXTFILEDES "
                    + ",      GUID "
                    + ",      CURDATE "
                    + ",      SIGNED ) "
                    + "VALUES ( {} "
                    + ",       '{}' "          
                    + ",        {}  "
                    + ",        {}  "
                    + ",       '{}' "
                    + ",       '{}' "
                    + ",       '{}' "
                    + ",        {} "
                    + ",       '{}' )"                    
                ).format( row2[0] 
                    , '~'
                    , self.qrField("CAT")
                    , row2[1] 
                    , self.url 
                    , 'From ' + self.device
                    , self.uid 
                    , (datetime.date.today() - datetime.date(1988, 1, 1)).total_seconds() / 60 
                    , self.preauthStr()
                )                     
                # print(sql)                  
                ret = cursor3.execute( sql )                
                cursor3.close()

            cursor2.close

        cursor.close()
        cnxn.commit()
        cnxn.close()

    def qrField(self, field):
        for i in [i for i in self.qrdata if i['i'].lower() == field.lower()]: return i['v']
    
    def preauthStr(self):
        match self.preauth:
            case True : return "Y"
            case _    : return ""

class Page:
    def __init__(self, pageid , path):
        self.pageid = pageid
        self.path = os.path.abspath(path)
        self.barcode = []            
        self.inbuff = []
        for barcode in decode(cv2.imread(self.path)) :                        
            try:
                if barcode.type == "QRCODE":
                    data = json.loads(barcode.data.decode())
                    for i in data["in"]:
                        self.inbuff.append(i)
            except  : pass    
            finally : self.barcode.append(barcode)
    
    def preauth(self):
        for i in [i for i in self.inbuff if i['i']=='PREAUTH']: return True

class file:
    def __init__(self, fname):                
        self.fname = fname
        self.device = fname.parent.name
        self.filename = fname.stem
        self.thisuser = ''
        self.thisdate = ''        
        self.pages = []        
        self.PDFfiles = []
        self.hascanvas = False
        self.NewestPage = datetime(1988, 1, 1)

        self.err = False
        if fname.stem.count('_')>0:        
            self.thisuser = fname.stem.split('_')[0]        
            self.thisdate = fname.stem.split('_')[1]                    
            self.AddPage(fname)

        else:
            self.err = True                

    def Wait(self):
        return self.NewestPage > datetime.now() - timedelta(minutes=2)
    
    def Compare(self, file):
        return file.device == self.device and file.thisdate == self.thisdate and file.thisuser == self.thisuser
    
    def AddPage(self, i):     
        if datetime.fromtimestamp(os.path.getmtime(i._str)) > self.NewestPage: 
            self.NewestPage = datetime.fromtimestamp(os.path.getmtime(i._str))
        if i.stem.count('_')==2:                    
            self.pages.append( Page(int(i.stem.split('_')[2]) , i))
        else:            
            self.pages.append(Page(1 , i))

    def NextPage(self, p=0):
        sa = []
        for q in [q for q in self.pages if q.pageid > p]:
            sa.append(q.pageid)
        if len(sa) > 0:
            for q in [q for q in self.pages if q.pageid == min(sa)]:            
                    return q
    
    def delPages(self):
        for q in self.pages:
            os.remove(q.path)
            
    def CreatePDF(self, p , preauth = False):
        self.hascanvas = True        
        pdf = PDFfile(self , p , preauth)        
        self.PDFfiles.append(pdf)
        return canvas.Canvas(pdf.path, pagesize=A4, pageCompression=1)
    
    def AppendPDF(self, p, c):
        c.drawInlineImage(p.path, inch*.25, inch*.25, PAGE_WIDTH-(.5*inch), PAGE_HEIGHT-(.316*inch))