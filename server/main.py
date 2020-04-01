import socket
import threading
import time
import random


class Client(threading.Thread):
    def __init__(self, numero):
        threading.Thread.__init__(self)
        self.numero = numero

    def run(self):
        client(self.numero)


def client(numero):
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    possibility = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    try:
        mysocket.connect(('127.0.0.1', 8000))
        mysocket.send('Client {0}'.format(numero).encode())
        print('Je suis le joueur : {0}'.format(mysocket.recv(64).decode()))
        data = mysocket.recv(64).decode()
        size, position = data.split(';')
        print('La grille est de {0} et je suis en {1}'.format(size, position))
        while True:
            mysocket.send(random.choice(possibility).encode())
            # mysocket.send('LFT'.encode())
            # mysocket.send("YOLO".encode()) # Test de message incorrect
            # mysocket.close() # Test pour faire crasher la socket cote serveur
            data = mysocket.recv(64).decode()
            # time.sleep(5.0) # Test de timeout
            print("Joueur {num} : {data}".format(num = numero, data = data)) # Affichage du retour
    except Exception as e:
        print(e)
        print('MORT')
        mysocket.close()


if __name__ == '__main__':
    try:
        for i in range(4):
            thread = Client(i)
            thread.daemon = True
            thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Fin du programme')
