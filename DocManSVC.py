import win32serviceutil , debugpy
from MedatechUK.APY.svc import AppSvc
from pathlib import Path
from scanfile import file
from connect import Drive

class MySVC(AppSvc):    

    _svc_name_ = "DocManSVC"
    _svc_display_name_ = "MedatechUK DocScan Manager"      
    _svc_description = "MedatechUK Barcoded scanned Document Manager by Si."

    def __init__(self , args):    
        self.Main = MySVC.main   
        self.Init = MySVC.init   
        self.Folder = Path(__file__).parent         
        AppSvc.__init__(self , args)

    def init(self):
        if self.debuginit: debugpy.breakpoint() 

        d = Drive([
            self.config.file.path[0:1].upper()
            , self.config.file.savedir[0:1].upper()
            ]) # Build Azure Connection
        if not d.Exists(): d.Connect()  # Connect Azure drive    

        self.log.logger.info("Searching for [{}] in [{}]...".format( 
            self.config.file.suffix
            , self.config.file.path
        ))    
        
    def main(self):     
        if self.debug: debugpy.breakpoint() 

        files = [] # Files in [file].path with [file].suffix
        for f in [f for f in Path(self.config.file.path).glob('**/*') if f.is_file() and f.suffix in self.config.file.suffix]:   
            fi = file(f, self)  
            if not fi.err: # Validate file syntax
                ad = True
                for i in files:
                    if i.Compare(fi): # File is in a set?
                        i.AddPage(f) # Add page to file
                        ad = False
                        break  
                if ad: files.append(fi) # Add New file
                    
        for f in [ f for f in files if not f.Wait() ]: # Pages > 2mins old 
            PREAUTH = False # Found a PREAUTH QR?
            p = f.NextPage() # Get First Page of file
            while p != None: # while has Page
                if p.preauth(): PREAUTH = True # Check page for PREAUTH 
                if p.barcode and not p.preauth(Only=True): # Page has Barcode?
                    if f.hascanvas: c.save() # Save previous PDF                     
                    c = f.CreatePDF(p , preauth=PREAUTH) # New PDF where PREAUTH !NOT only QR
                    f.AppendPDF(p , c) # Write page to PDF
                elif p.preauth(Only=True): 
                    pass
                elif f.hascanvas: # No barcode
                    c.showPage() # Add page break
                    f.AppendPDF(p , c) # Write page to PDF
                p = f.NextPage(p.pageid) # Get next page in file
            if f.hascanvas: c.save() # Save current PDF
            
            for pdf in f.PDFfiles: # PDFs in this file
                match pdf.hasqr :  # Has QR Data? 
                    case True   : 
                        if pdf.dbSavePayCard() : f.delPages()  # Save to CoW/Payement 
                    case _      : 
                        if pdf.dbSave() : f.delPages() # Save PDF to any Document
            
if __name__ == '__main__':    
    win32serviceutil.HandleCommandLine(MySVC)    