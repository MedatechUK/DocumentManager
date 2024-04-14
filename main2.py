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
