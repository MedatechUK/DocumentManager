#region "Imports"

# System Imports
import json , os , uuid , pyodbc 
from pathlib import Path
from datetime import *

# Barcode Imports
import cv2 
from pyzbar.pyzbar import decode 

# PDF Imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize

PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]

# Medatech Imports
from MedatechUK.mLog import mLog 
from MedatechUK.oDataConfig import Config
from MedatechUK.apy import Response

# Local Imports
import oTrans

#endregion

class PDFfile:
    def __init__(self, f , p , preauth, svc): 
        self.svc = svc       
        self.uid = str(uuid.uuid4())
        self.folder = svc.config.file.savedir 
        self.path = os.path.join(self.folder , self.uid + ".pdf")
        self.device = f.device
        self.thisuser = f.thisuser
        self.thisdate = f.thisdate
        self.barcode = p.barcode
        self.preauth = preauth
        self.url = svc.config.file.saveurl.format(self.uid + ".pdf")
        self.qrdata = p.inbuff
        self.hasqr = len(p.inbuff) > 0
    
    def dbSave(self):
        try :
            for b in self.barcode:        
                r = Response()                  # Create an object to hold the result
                q = oTrans.DOC(uid = self.uid   # Create Transaction
                    , barcode = b.data.decode()            
                    , url = self.url 
                    , user = self.thisuser
                    , prn = self.device
                )        
                q.toPri(                        # Send this object to Priority
                    self.svc.oDataConfig
                    , q.toFlatOdata 
                    , response = r
                )
            return True
        except: return False

    def dbSavePayCard(self):
        try:
            r = Response()                      # Create an object to hold the result
            q = oTrans.CoW(uid = self.uid       # Create Transaction
                , fix = self.qrField("PROJACT") 
                , cat = self.qrField("CAT")
                , preauth = self.preauthStr()
                , url = self.url 
                , user = self.thisuser
                , prn = self.device
            )        
            q.toPri(                            # Send this object to Priority
                self.svc.oDataConfig
                , q.toFlatOdata 
                , response = r
            )
            return True
        except: return False

    def qrField(self, field):
        for i in [i for i in self.qrdata if i['i'].lower() == field.lower()]: return i['v']
    
    def preauthStr(self):
        match self.preauth:
            case True : return "Y"
            case _    : return ""

class Page:
    def __init__(self, pageid , path):
        self.log = mLog()        
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
    
    def preauth(self , Only=False):
        if Only: 
            for i in [i for i in self.inbuff if i['i']!='PREAUTH']: return False
            self.log.logger.debug("PreAuth ONLY - Skip [{}].".format( self.path ))
            return True
        else:
            for i in [i for i in self.inbuff if i['i']=='PREAUTH']: 
                self.log.logger.debug("PreAuth Found.")
                return True
            return False

class file:
    def __init__(self, fname , svc):    
        
        self.log = mLog()
        self.fname = fname
        self.device = fname.parent.name
        self.filename = fname.stem
        self.thisuser = ''
        self.thisdate = ''        
        self.pages = []        
        self.PDFfiles = []
        self.hascanvas = False
        self.NewestPage = datetime(1988, 1, 1)
        self.svc = svc
        self.currentPDF = ""

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
        if p==0:
            self.log.logger.debug("Found [{}] page(s) scanned by [{}] on [{}]".format( len(sa) , self.thisuser , self.device))            

        if len(sa) > 0:
            for q in [q for q in self.pages if q.pageid == min(sa)]: 
                match p:
                    case 0 : self.log.logger.debug("First page is [{}].".format( str(q.pageid) ))
                    case _ : self.log.logger.debug("Next Page after [{}] is [{}].".format( str(p) , str(q.pageid) ))
                return q                   
        else: 
            self.log.logger.debug("Page [{}] is last page.".format( str(p) ))
            return None
    
    def delPages(self):
        for q in self.pages:
            self.log.logger.debug("Deleting Page: [{}]".format( q.path))
            os.remove(q.path)
            
    def CreatePDF(self, p , preauth = False):        
        self.hascanvas = True                
        pdf = PDFfile(self , p , preauth, self.svc) 
        self.currentPDF = pdf.path
        self.log.logger.debug("Create PDF: [{}]".format( pdf.path ))        
        self.PDFfiles.append(pdf)
        return canvas.Canvas(pdf.path, pagesize=A4, pageCompression=1)
    
    def AppendPDF(self, p, c):
        self.log.logger.debug("Add Page [{}] to PDF [{}]".format( p.path ,self.currentPDF ))
        c.drawInlineImage(p.path, inch*.25, inch*.25, PAGE_WIDTH-(.5*inch), PAGE_HEIGHT-(.316*inch))