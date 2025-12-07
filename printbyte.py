p = r"c:\Users\ibrahimoz\Desktop\Derleyici_ Tasarimi_Projesi\minilang.txt"
with open(p,'rb') as f:
    b = f.read()
print('BYTES REPR:')
print(repr(b))
print('\nDECODED REPR (utf-8):')
try:
    print(repr(b.decode('utf-8')))
except Exception as e:
    print('decode error:', e)
