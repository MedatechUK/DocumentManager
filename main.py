from pathlib import Path
from scanfile import file
from reportlab.pdfgen import canvas

PREAUTH = False # Found a PREAUTH QR?
files = [] # Jpeg files in s://
for f in [f for f in Path('s:/').glob('**/*') if f.is_file() and f.suffix =='.jpeg']:  
  fi = file(f)  
  if not fi.err: # Validate file syntax
    ad = True
    for i in files:
        if i.Compare(fi): # File is in a set?
           i.AddPage(f) # Add page to file
           ad = False
           break  
    if ad:
        files.append(fi) # Add New file

for f in [ f for f in files if not f.Wait() ]: # Newest page > 2mins old
    p = f.NextPage() # Get First Page of file
    while p: # while has Page
        if p.barcode: # Page has Barcode?
            if f.hascanvas: c.save() # Save old PDF 
            if p.preauth(): PREAUTH = True # Check page for PREAUTH
            c = f.CreatePDF(p , preauth=PREAUTH) # Create new PDF
        else: # No barcode
           if f.hascanvas: c.showPage() # Add page break
        if f.hascanvas: f.AppendPDF(p , c) # Write page to PDF
        p = f.NextPage(p.pageid) # Get next page in file
    if f.hascanvas: c.save() # Save current PDF
    
    for pdf in f.PDFfiles:
        match pdf.hasqr:
            case True   : pdf.dbSavePayCard() # Save PDF to Priority
            case _      : pdf.dbSave() # Save PDF to Priority
    # f.delPages() # Clean Jpegs