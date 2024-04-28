from MedatechUK.mLog import mLog , os 
from MedatechUK.oDataConfig import Config
from MedatechUK.apy import Response

from pathlib import Path 
import oTrans, json

log = mLog()
os.chdir(Path(__file__).parent)
log.start( os.getcwd(), "DEBUG" )
log.logger.debug("Starting {}".format(__file__) )

q = oTrans.CoW(fix = 1 # Create Transaction
    , cat = 2 
    , preauth = "Y"
    , url = "../../somrthing"
)

r = Response() # Create an object to hold the result
q.toPri(       # Send this object to Priority(    
    Config(
        env = "fuld1" 
        , path = os.getcwd()
    )
    , q.toFlatOdata 
    , response=r
)

pass