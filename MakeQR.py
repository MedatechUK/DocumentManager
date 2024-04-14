import pyqrcode
from PIL import Image

qrcode = pyqrcode.create('{"in":[{"i":"PROJACT","v":3411},{"i":"CAT","v":14}]}')
qrcode.png('pr3411cow.png',scale=8)
qrcode = pyqrcode.create('{"in":[{"i":"PROJACT","v":3411},{"i":"CAT","v":13}]}')
qrcode.png('pr3411pc.png',scale=8)