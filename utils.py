import sys
import time
import itertools
import threading
from os import walk, getcwd, path


class Loading():
    __isStart = True
    loadtxt = 'Loading...'
    def __animate(self):
        for c in itertools.cycle([' |', ' /', ' -', ' \\']):
            if not self.__isStart: 
                break
            sys.stdout.write('\r' + self.loadtxt + c)
            sys.stdout.flush()
            time.sleep(0.1)

    def start(self, loadtxt):
        self.__isStart = True
        self.loadtxt = loadtxt
        t = threading.Thread(target=self.__animate)
        t.start()

    def stop(self, stoptxt):
        self.__isStart = False
        sys.stdout.write('\r' + stoptxt + '                   ')
        sys.stdout.flush()
        print()


def ls(ruta=getcwd()):
    listaarchivos = []
    for (dir, _, archivos) in walk(ruta):
        listaarchivos.extend([path.join(dir, arch) for arch in archivos])
    return listaarchivos
