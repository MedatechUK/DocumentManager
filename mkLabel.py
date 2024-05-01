import labels
import pyqrcode
from reportlab.graphics import shapes
from MedatechUK.oDataConfig import Config
from MedatechUK.cl import clArg
import os

class ConfQR:
    def __init__(self, **kwargs):
        self.projact = kwargs['projact']            
        self.cat = kwargs['cat']                        
        self.des = kwargs['des']                

def draw_label(label, width, height, obj):
    # Just convert the object to a string and print this at the bottom left of
    # the label.    

    qrcode = pyqrcode.create("{'in':[{'i':'PROJACT','v':"+ str(obj.projact) +",{'i':'CAT','v': "+ str(obj.cat) + "}]}")                             
    qrcode.png('qr.png',scale=8)

    label.add ( shapes.Image ( 3 , 5 , width-3, height-1, 'qr.png' ))
    label.add ( shapes.String ( 16, 2, str(obj.des), fontName="Helvetica", fontSize=12 ))

arg = clArg()
if arg.byName(["site"])==None:
    print ("No site specified.")
    exit
    
# Create the sheet.
# Create an A4 portrait (210mm x 297mm) sheets with 4 columns and 8 rows of
# labels. Each label is 30mm x 30mm with a 2mm rounded corner. The margins are
# automatically calculated.
specs = labels.Specification(210, 297, 4, 8, 30, 30, corner_radius=2)
sheet = labels.Sheet(specs, draw_label, border=True)

settingsini = os.getcwd() + "\\settings.ini"        
config = Config(
    env = 'test'
    , path = os.getcwd()
)
cnxn = Config.cnxn(config)
cursor = cnxn.cursor() 
cursor.execute("USE [{}]; ".format(config.config.odata.env))    
sql = ("select PROJACT ,  14 , WBS "
    + "from PROJACTS "
    + "join DOCUMENTS on DOCUMENTS.DOC = PROJACTS.DOC "
    + "join system.dbo.ZCLA_FIXES on PROJACTS.ZCLA_FIX = ZCLA_FIXES.FIXID "
    + "where 0=0 "
    + "AND   DOCUMENTS.DOCNO = '{}' "
    + "AND   PROJACTS.T$LEVEL = 3 "
    + "AND   ZCLA_FIXES.ISPAYMENT = 'Y' "
    + "AND   ZCLA_FIXES.FIX < 99 ").format(arg.byName(["site"])) 

iv = cursor.execute(sql)            
for row in iv:      
    sheet.add_label( ConfQR( projact=int(row[0]) , cat=int(row[1]) , des=row[2] ) )

cursor.close()
sheet.save('{}.pdf'.format(arg.byName(["site"])))