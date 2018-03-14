import keras
import shutil
from keras.models import Model
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import model_from_json
from os import walk, getcwd, path
from time import time
import numpy as np
import sys
import argparse
from tqdm import tqdm

vervose = False
tiempo_inicial_proceso = time()


def ls(ruta=getcwd()):
    listaarchivos = []
    print('Buscando archivos... Por favor espere!')
    for (dir, _, archivos) in walk(ruta):
        listaarchivos.extend([path.join(dir, arch) for arch in archivos])
    return listaarchivos


def OpenNsfw(weight_file="max_open_nsfw.h5"):
    if vervose:
        print('\nCargando modelo...\n')
    json_file = open('max_open_nsfw.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    if vervose:
        print('\nModelo cargado...\nConfigurando modelo...\n')
    model.load_weights(weight_file)
    if vervose:
        print('\nModelo cargado y configurado!\n')
    return model


def isPorno(model, img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    return preds[0][1]


def procesarArchivo(img_path):
    model = OpenNsfw()
    try:
        resultado = 0.00
        resultado = isPorno(model, img_path)
        print('La probabilidad de que:\n', img_path,
              '\nSea porno es de %.2f' % (resultado * 100), '%\n')
    except(OSError, ValueError):
        print(img_path, '\nNo es un archivo de imagen valido!\n')


def procesarDirectorio(dir):
    model = OpenNsfw()
    nroArchivo = 0
    errores = 0
    files = ls(dir)
    print('Examinando...\n')
    for f in tqdm(files, total=len(files), unit=' archivos',leave=False):
        img_path = f
        msg = ''
        nroArchivo = nroArchivo + 1
        try:
            resultado = isPorno(model, img_path)
            msg = 'Probabilidad: ' + str(round(resultado * 100, 2)) + ' %'
        except(OSError, ValueError):
            errores = errores + 1
            msg = 'No es un imagen valida!'
            continue
        finally:
            msg = '\r' + img_path + ' ' + msg  + '\r\f'
            #print( msg,end='\f',flush=True)
    print('\nTotal Archivos: ', nroArchivo)
    print('Total Archivos invalidos: ', errores)
    print('Total Imagenes Analizadas: ', nroArchivo - errores)


if (__name__ == '__main__'):

    tiempo_inicial = time()
    parser = argparse.ArgumentParser(
        description='Detectar imagenes pornograficas.')
    parser.add_argument('ruta', metavar='path',
                        help='"Imagen" o Directorio a testear.')
    parser.add_argument('-s', '--score', action='store_true',
                        help='Reduce image size to increase speed of scanning')
    parser.add_argument('-v', '--vervose', action='store_true',
                        help='Mostrar detalles del proceso.')

    args = parser.parse_args()

    ruta = args.ruta
    if(args.vervose):
        vervose = True
    if(path.isfile(ruta)):
        procesarArchivo(ruta)
    elif (path.isdir(ruta)):
        procesarDirectorio(ruta)
    else:
        print('Archivo o Directorio incorrecto!')

    tiempo_total = time() - tiempo_inicial
    hs, min, seg = (abs(tiempo_total / 3600),
                    abs(tiempo_total / 60), tiempo_total % 60)
    print('\nTiempo total: %d:%d:%d h:m:s' % (hs, min, seg))
