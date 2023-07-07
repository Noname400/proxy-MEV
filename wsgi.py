from proxy import app

from sys import argv

if __name__ == "__main__":
    net = argv[1]
    
    if net == 'test': (f'[I] Запущена тестовая сеть')
    else: print('[I] Запущена основная сеть')
    
    app.run()