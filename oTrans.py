from MedatechUK.Serial import SerialBase , SerialT , SerialF

class CoW(SerialBase) :
    #region "Properties"
    @property
    def fix(self):    
        return self._fix
    @fix.setter
    def fix(self, value):
        self._fix = value

    @property
    def cat(self):    
        return self._cat
    @cat.setter
    def cat(self, value):
        self._cat = value

    @property
    def preauth(self):    
        return self._preauth
    @preauth.setter
    def preauth(self, value):
        self._preauth = value        

    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, value):
        self._url = value

    @property
    def user(self):
        return self._user
    @user.setter
    def user(self, value):
        self._user = value

    @property
    def prn(self):
        return self._prn
    @prn.setter
    def prn(self, value):
        self._prn = value

    @property
    def uid(self):
        return self._uid
    @uid.setter
    def uid(self, value):
        self._uid = value

    #endregion
        
    #region "Ctor"
    def __init__(self,  **kwargs): 	        
        self.fix =  0
        self.cat =  0
        self.preauth =  ""
        self.url = ""
        self.user = ""
        self.prn = ""
        self.uid = ""

        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1, typename="COW"), **kwargs)
        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")
        SerialT(self, "fix" , pCol="INT1" , pType="INT")
        SerialT(self, "cat" , pCol="INT2" , pType="INT")
        SerialT(self, "preauth" , pCol="TEXT3" , pType="CHAR")
        SerialT(self, "url" , pCol="TEXT21" , pType="CHAR")
        SerialT(self, "uid" , pCol="TEXT22" , pType="CHAR")
        SerialT(self, "user" , pCol="TEXT1" , pType="CHAR")
        SerialT(self, "prn" , pCol="TEXT2" , pType="CHAR")

    #endregion

class DOC(SerialBase) :
    #region "Properties"
    @property
    def barcode(self):    
        return self._barcode
    @barcode.setter
    def barcode(self, value):
        self._barcode = value      

    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, value):
        self._url = value

    @property
    def user(self):
        return self._user
    @user.setter
    def user(self, value):
        self._user = value

    @property
    def prn(self):
        return self._prn
    @prn.setter
    def prn(self, value):
        self._prn = value

    @property
    def uid(self):
        return self._uid
    @uid.setter
    def uid(self, value):
        self._uid = value

    #endregion
        
    #region "Ctor"
    def __init__(self,  **kwargs): 	        
        self.barcode = ""
        self.url = ""
        self.user = ""
        self.prn = ""
        self.uid = ""

        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1, typename="DOC"), **kwargs)
        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")        
        SerialT(self, "url" , pCol="TEXT20" , pType="CHAR")
        SerialT(self, "uid" , pCol="TEXT21" , pType="CHAR")
        SerialT(self, "user" , pCol="TEXT1" , pType="CHAR")
        SerialT(self, "prn" , pCol="TEXT2" , pType="CHAR")
        SerialT(self, "barcode" , pCol="TEXT3" , pType="CHAR")

    #endregion
                