import urllib.parse
password = "G^qjC7F$@P65DqpN*mmv"
encoded = urllib.parse.quote(password, safe='')
print(f"Original: {password}")
print(f"Encoded:  {encoded}")
