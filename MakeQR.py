import pyqrcode
from PIL import Image

qrcode = pyqrcode.create('{"in":[{"i":"PREAUTH"}]}')
qrcode.png('preauth.png',scale=8)