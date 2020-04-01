from tkinter import *
from tkinter.messagebox import showinfo
import socket
import random
import time


class Server:
    def __init__(self, canvas, size, gridSize):
        self.canvas = canvas
        self.size = size
        self.gridSize = gridSize
        self.contestants = []
        self.grid = [[]]
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptableMsg = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        self.alive = 4

    def waitForClient(self):
        self.grid = [[-1 for _ in range(self.gridSize)] for _ in range(self.gridSize)]
        startPosition = [(int(len(self.grid) / 2), 0),  # En haut
                         (0, int(len(self.grid[0]) / 2)),  # A gauche
                         (int(len(self.grid) / 2), int(len(self.grid[0]) - 1)),  # En bas
                         (int(len(self.grid) - 1), int(len(self.grid[0]) / 2))]  # A droite

        try:
            print("En attente des clients")
            self.serversocket.bind(('', 8000))
            self.serversocket.listen(4)
            socket.setdefaulttimeout(1)
            while len(self.contestants) < 4:
                print("En attente de connexion du joueur {0}".format(len(self.contestants)))
                (clientsocket, address) = self.serversocket.accept()

                name = clientsocket.recv(64).decode()
                clientsocket.send(str(len(self.contestants)).encode())

                de = ("%02x" % random.randint(0, 255))
                re = ("%02x" % random.randint(0, 255))
                we = ("%02x" % random.randint(0, 255))
                ge = "#"
                color = ge + de + re + we

                contestant = dict(name=name, socket=clientsocket, alive=True,
                                  position=startPosition[len(self.contestants)], color=color)

                self.grid[contestant['position'][0]][contestant['position'][1]] = 1

                if len(self.contestants) == 0:
                    textPosition = (
                    startPosition[len(self.contestants)][0] * size + 60, startPosition[len(self.contestants)][1] * size + 35)
                elif len(self.contestants) == 1:
                    textPosition = (
                    startPosition[len(self.contestants)][0] * size + 30, startPosition[len(self.contestants)][1] * size + 50)
                elif len(self.contestants) == 2:
                    textPosition = (
                    startPosition[len(self.contestants)][0] * size + 60, startPosition[len(self.contestants)][1] * size + 70)
                else:
                    textPosition = (
                    startPosition[len(self.contestants)][0] * size + 100, startPosition[len(self.contestants)][1] * size + 50)

                contestant['text'] = canvas.create_text(textPosition[0], textPosition[1], text=name, fill=color)

                self.contestants.append(contestant)
                setColor(canvas, size, contestant)

                print("{0} (from : {1}) rejoins la game !".format(name, address))
                contestant['socket'].send("{0}:{1};{2}:{3}".format(len(self.grid), len(self.grid[0]), contestant['position'][0],
                                                                   contestant['position'][1]).encode())

            print("Tous les joueurs sont là")

        except Exception as e:
            print(e)
        finally:
            self.canvas.after(ms=2000, func=self.play)

    def play(self):

        if self.alive > 1:
            print('Il reste {0} joueur(s) en vie !'.format(self.alive))
            updateString = ""
            # boucle de réception
            for contestant in self.contestants:
                if contestant['alive']:
                    try:
                        message = contestant['socket'].recv(64).decode().upper()
                        move = (0, 0)
                        if message not in self.acceptableMsg:
                            raise ValueError('Erreur de donnée', message)
                        else:
                            if message == 'UP':
                                move = (0, -1)
                            elif message == 'DOWN':
                                move = (0, 1)
                            elif message == 'LEFT':
                                move = (-1, 0)
                            elif message == 'RIGHT':
                                move = (1, 0)

                            if not moveContestant(self.grid, contestant, move):
                                print('Le joueur {0} est mort'.format(contestant['name']))
                                contestant['alive'] = False
                                self.alive = self.alive - 1
                                canvas.itemconfigure(contestant['text'], fill='black')

                        setColor(self.canvas, self.size, contestant)

                    except ValueError:
                        try:
                            contestant['socket'].send(
                                "FORFAIT \"{0}\" n'est pas une entrée valide".format(message).encode())
                            print('{0} est disqualifié (Raison: Message incorrect)'.format(contestant['name']))
                            contestant['alive'] = False
                            self.alive = self.alive - 1
                            canvas.itemconfigure(contestant['text'], fill='magenta')
                        except:
                            print('{0} est partis (Disconnect)'.format(contestant['name']))
                            contestant['alive'] = False
                            self.alive = self.alive - 1
                            canvas.itemconfigure(contestant['text'], fill='red')

                    except socket.error:
                        print('Timeout de {0}'.format(contestant['name']))
                        contestant['alive'] = False
                        self.alive = self.alive - 1
                        canvas.itemconfigure(contestant['text'], fill='red')

                updateString += '{0}:{1};'.format(contestant['position'][0], contestant['position'][1])

            updateString = updateString[:-1]  # On retire le dernier ;

            # boucle d'update client
            for contestant in self.contestants:
                if contestant['alive']:
                    contestant['socket'].send(updateString.encode())
            self.canvas.after(ms=1000, func=self.play)
        else:
            winner = tuple((contestant for contestant in self.contestants if contestant['alive']))
            if len(winner):
                print('Le joueur {0} a gagné !'.format(winner[0]['name']))
                showinfo(title='Tron Server', message='{0} a gagné'.format(winner[0]['name']))
            else:
                print('ILS SONT TOUS MOOOOOOORTS')
                showinfo(title='Tron Server', message='ILS SONT TOUS MORTS !')


def setColor(canvas, size, contestant):
    if contestant['alive']:
        color = contestant['color']
    else:
        color = "#000000"

    canvas.create_rectangle(contestant['position'][0] * size+60, contestant['position'][1] * size+50,
                            (contestant['position'][0] + 1) * size+60,
                            (contestant['position'][1] + 1) * size+50,
                            fill=color)


def moveContestant(grid, contestant, move):
    destination = tuple(map(sum, zip(contestant['position'], move)))
    possible = True

    if min(destination) < 0 or max(destination) >= len(grid):
        possible = False
    elif grid[destination[0]][destination[1]] == -1:  # Si personne n'est passé, alors c'est bon
        grid[destination[0]][destination[1]] = 1
    else:
        possible = False

    contestant['position'] = destination
    return possible


if __name__ == '__main__':
    root = Tk()
    root.title('LiveView')

    size = 8
    gridSize = 75
    canvas = Canvas(root, width=(size+1)*gridSize+50, height=(size+1)*gridSize+50, bg='white')
    canvas.pack()
    for i in range(gridSize+1):
        x = i * size
        canvas.create_line(x+60, (size*gridSize) + 50, x+60, 50, width=1)

    for i in range(gridSize+1):
        y = -i * size
        canvas.create_line((size*gridSize) + 60, -y+50, 60, -y+50)

    try:
        serverThread = Server(canvas=canvas, size=size, gridSize=gridSize)
        canvas.after(ms=1000, func=serverThread.waitForClient)

        root.mainloop()

    except KeyboardInterrupt:
        print("ON FERME TOUT")

    finally:
        root.quit()
        serverThread.serversocket.close()

