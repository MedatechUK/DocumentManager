import os
import uuid
from pathlib import Path
import datetime

import pyodbc 

import cv2 
from pyzbar.pyzbar import decode 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize

PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]

class PDFfile:
    def __init__(self, f , p):        
        self.uid = str(uuid.uuid4())
        self.folder = "f://scans//"        
        self.path = os.path.join(self.folder , self.uid + ".pdf")
        self.device = f.device
        self.thisuser = f.thisuser
        self.thisdate = f.thisdate
        self.barcode = p.barcode
        self.url = "../../system/mail/scans/{}".format(self.uid + ".pdf")
        
    def dbSave(self):
        SERVER = 'CE-AZ-UK-S-PRIO'
        INSTANCE = 'TST'
        DATABASE = 'fuld1'
        USERNAME = 'tabula'
        PASSWORD = 'cheese8!'
        # dr = pyodbc.drivers()
        cnxn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER}\\{INSTANCE};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};MARS_Connection=Yes')
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

class Page:
    def __init__(self, pageid , path):
        self.pageid = pageid
        self.path = os.path.abspath(path)
        self.barcode = []            
        for barcode in decode(cv2.imread(self.path)) :                  
            self.barcode.append(barcode)

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

        self.err = False
        if fname.stem.count('_')>0:        
            self.thisuser = fname.stem.split('_')[0]        
            self.thisdate = fname.stem.split('_')[1]                    
            self.AddPage(fname)

        else:
            self.err = True                

    def Compare(self, file):
        return file.device == self.device and file.thisdate == self.thisdate and file.thisuser == self.thisuser
    
    def AddPage(self, i):     
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
            
    def CreatePDF(self, p):
        self.hascanvas = True
        pdf = PDFfile(self , p)        
        self.PDFfiles.append(pdf)
        return canvas.Canvas(pdf.path, pagesize=A4)
    
    def AppendPDF(self, p, c):
        c.drawInlineImage(p.path, inch*.25, inch*.25, PAGE_WIDTH-(.5*inch), PAGE_HEIGHT-(.316*inch))