import json

f = open("qr.json")
try:
    data = json.load(f)
    for i in data["in"]:
        print(i['i'], i['v'])
except:
    print("No JSON")            
finally:
    f.close