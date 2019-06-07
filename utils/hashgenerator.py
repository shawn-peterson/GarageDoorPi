import hashlib
myPassword=b"updown"
print(hashlib.sha256(myPassword).hexdigest())