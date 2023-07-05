s = 'abs.jpg'
print(s[:s.index('.')+1]+'png' if s[s.index('.')+1:] != 'png' else s)