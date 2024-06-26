from pathlib import Path
from scanfile import file
from reportlab.pdfgen import canvas
from connect import Drive
from MedatechUK.APY.mLog import mLog , os

log = mLog()
os.chdir(Path(__file__).parent)
log.start( os.getcwd(), "DEBUG" )
log.logger.debug("Starting {}".format(__file__) )

d = Drive()
if not d.Exists():
    if not d.Connect(): print(d.err)            
else: print("Remote Drive Connected!")

PREAUTH = False # Found a PREAUTH QR?
files = [] # Jpeg files in s://
for f in [f for f in Path('s:/').glob('**/*') if f.is_file() and f.suffix =='.jpeg']:  
  fi = file(f , log.logger)  
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