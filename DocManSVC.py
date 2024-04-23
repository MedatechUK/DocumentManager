import win32serviceutil , win32service , win32event, servicemanager
from pathlib import Path
from time import sleep
from reportlab.pdfgen import canvas
from scanfile import file
from connect import Drive
from MedatechUK.mLog import mLog , os 

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "DocManSVC"
    _svc_display_name_ = "Document Scan Manager"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        self.stop = False
        
        self.log = mLog()
        os.chdir(Path(__file__).parent)
        self.log.start( os.getcwd(), "DEBUG" )
        self.log.logger.debug("Starting {}".format(__file__) )
            
    def SvcStop(self):
        self.log.logger.debug("Service Stopping...")       
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop = True

    def SvcDoRun(self):
        self.log.logger.debug("Service Starting...")      
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))        

        self.main()

    def main(self):                           
        
        d = Drive() # Connect Azure drive
        if not d.Exists():
            if not d.Connect(): 
                self.log.logger.warn(d.err)         
                self.stop = True
            else: self.log.logger.debug("Remote Drive Connected!")
        else: self.log.logger.debug("Remote Drive Connected!")
        
        if not self.stop: self.log.logger.debug("Service Running...")    
        while not self.stop:                       
            sleep(5)                        
            files = [] # Jpeg files in s://
            for f in [f for f in Path('s:/').glob('**/*') if f.is_file() and f.suffix =='.jpeg']:   
                fi = file(f, self.log.logger)  
                if not fi.err: # Validate file syntax
                    ad = True
                    for i in files:
                        if i.Compare(fi): # File is in a set?
                            i.AddPage(f) # Add page to file
                            ad = False
                            break  
                    if ad:
                        files.append(fi) # Add New file
                        
            for f in [ f for f in files if not f.Wait() ]: # Pages > 2mins old 
                PREAUTH = False # Found a PREAUTH QR?
                p = f.NextPage() # Get First Page of file
                while p != None: # while has Page
                    if p.barcode: # Page has Barcode?
                        if f.hascanvas: c.save() # Save previous PDF 
                        if p.preauth(): PREAUTH = True # Check page for PREAUTH 
                        if not p.preauth(Only=True): c = f.CreatePDF(p , preauth=PREAUTH) # New PDF where PREAUTH !NOT only QR
                    else: # No barcode
                        if f.hascanvas: c.showPage() # Add page break
                    if f.hascanvas: f.AppendPDF(p , c) # Write page to PDF
                    p = f.NextPage(p.pageid) # Get next page in file
                if f.hascanvas: c.save() # Save current PDF
                
                for pdf in f.PDFfiles: # PDFs in this file
                    match pdf.hasqr: # Has QR Data? 
                        case True   : pdf.dbSavePayCard() # Save to CoW/Payement 
                        case _      : pdf.dbSave() # Save PDF to any Document
                f.delPages() # Clean used Jpegs

if __name__ == '__main__':    
    win32serviceutil.HandleCommandLine(AppServerSvc)