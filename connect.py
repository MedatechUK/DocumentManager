import subprocess
import string , os
from ctypes import windll
from MedatechUK.mLog import mLog 

class Drive:
    def __init__(self , letter):
        self.log = mLog()
        self.letter = letter
        self.drives = []
        self.GetDrives()                
        self.err = ""

    def Exists(self):
        for i in [ i for i in self.drives if i.lower()==(self.letter.lower())] : return True
        return False
    
    def Connect(self):        
        f = open(os.getcwd() + "//connect.ps", "r")  
        cmd = f.read()     
        f.close
        proc = subprocess.run (
            args = [
            'powershell' ,
            '-noprofile' ,
            '-command' , 
            cmd ],
            text = True ,
            stdout = subprocess.PIPE
        )        
        
        self.GetDrives()        
        if not self.Exists():
            self.log.logger.critical(proc.stdout)         
            raise "Could not connect to Remote Drive."
        else: self.log.logger.info("Remote Drive Connected!") 

    def GetDrives(self):
        self.drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                self.drives.append(letter)
            bitmask >>= 1    