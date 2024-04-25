import subprocess
import string , os
from ctypes import windll

class Drive:
    def __init__(self):
        self.drives = []
        self.GetDrives()        
        self.letter = "S"
        self.err = ""

    def Exists(self):
        for i in [ i for i in self.drives if i==(self.letter)] : return True
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
        self.err = proc.stdout
        self.GetDrives()
        return self.Exists()
    
    def GetDrives(self):
        self.drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                self.drives.append(letter)
            bitmask >>= 1    