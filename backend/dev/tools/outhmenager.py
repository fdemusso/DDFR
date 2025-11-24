import hashlib

s = input("Inserisci la password da hashare: ")
res = hashlib.md5(s.encode())
print(f"Inserire in .env: {res.hexdigest()}")