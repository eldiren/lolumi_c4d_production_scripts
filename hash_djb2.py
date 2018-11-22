import c4d
from c4d import gui
#Welcome to the world of Python

def hash_djb2(s):                                                                                                                                
    hash = 5381
    for x in s:
        hash = (( hash << 5) + hash) + ord(x)
    return hash & 0xFFFFFFFF

def main():
    print hash_djb2("Black Lagoon Lizardman")

if __name__=='__main__':
    main()
