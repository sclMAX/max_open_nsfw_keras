import keras
from keras.models import Model
from keras import layers
import keras.backend as K
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import model_from_json
from os import walk, getcwd, path
from time import time


def ls(ruta=getcwd()):
    listaarchivos = []
    for (dir, _, archivos) in walk(ruta):
        listaarchivos.extend([path.join(dir, arch) for arch in archivos])
    yield listaarchivos


import numpy as np
import sys


def OpenNsfw(weight_file="max_open_nsfw.h5"):
    json_file = open('max_open_nsfw.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(weight_file)
    return model


def isPorno(model, img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    return preds[0][1]


if __name__ == '__main__':
    print('\nCargando modelo....\n')
    tiempo_inicial = time()
    model = OpenNsfw()
    ruta = sys.argv[1]
    print('\nModelo cargado con exito!\n Buscando Archivos...\n')
    archivos = ls(ruta)
    #print('Archivos encontrados: %1d Iniciando escaneo...\n' % (archivos.mro))
    nroArchivo = 0
    errores = 0
    tiempo_inicial_proceso = time()
    for f in next(archivos):
        img_path = f
        nroArchivo = nroArchivo + 1
        print('Escaneando archivo %2d... Tiempo: %.2f seg.' %
              (nroArchivo, time() - tiempo_inicial))
        try:
            resultado = 0.00
            resultado = isPorno(model, img_path)
            print('La probabilidad de que:\n', img_path,
                  '\nSea porno es de %.2f' % (resultado * 100), '%\n')
        except(OSError, ValueError):
            print(img_path, '\nNo es un archivo de imagen valido!\n')
            errores = errores + 1
            continue
        except:
            print(img_path, '\nNo es un archivo de imagen valido!\n')
            errores = errores + 1
            continue

    tiempo_final = time()

    tiempo_total = tiempo_final - tiempo_inicial
    tiempo_proceso = tiempo_final - tiempo_inicial_proceso

    print('Tiempo total: %.2f seg. ,Tiempo proceso: %.2f seg. ,Errores: %1d ,Total de images procesadas: %1d ,Total Archivos: %1d\n' % (
        tiempo_total, tiempo_proceso, errores, nroArchivo - errores,  nroArchivo))
