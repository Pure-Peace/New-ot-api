def log(text, color='w'):
    d = {'b': 30,'r': 31,'g': 32,'y': 33,'b': 34,'m': 35,'c': 36,'w': 37}
    print(f'\033[1;{d[color]}m{text}\033[0m')
