import keras
import shutil
import json
import utils
from keras.models import Model
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import model_from_json
from time import time
import numpy as np
import sys
import argparse
from tqdm import tqdm
from os import path

score = 0.00
outFolder = '/'
createMin = False
tiempo_inicial_proceso = time()
load = utils.Loading()

def OpenNsfw(weight_file="max_open_nsfw.h5"):
    load.start('Cargando modelo...')
    json_file = open('max_open_nsfw.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    load.stop('Modelo cargado!')
    load.start('Configurando modelo...')
    model.load_weights(weight_file)
    load.stop('Modelo configurado!')
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
    msg=''
    try:
        resultado = 0.00
        resultado = isPorno(model, img_path)
        msg = 'Probabilidad: ' + str(round(resultado * 100, 2)) + ' %'
    except(OSError, ValueError):
        msg = 'No imagen valida!'
    finally:
        msg = msg + '\t' + img_path
        print(msg)


def procesarDirectorio(dir):
    model = OpenNsfw()
    nroArchivo = 0
    excluidos = 0
    incluidas = 0
    errores = 0
    reporte = []
    load.start('Buscando archivos...')
    files = utils.ls(dir)
    load.stop('%d Archivos encontrados!' % (len(files)))
    msg = ''
    pbar = tqdm(
        files,
        total=len(files),
        desc=' Examinando',
        unit=' archivos',
        leave=False,
        dynamic_ncols=True
    )
    for f in pbar:
        img_path = f
        nroArchivo += 1
        try:
            resultado = isPorno(model, img_path)
            if(resultado >= score):
                msg = 'Probabilidad: ' + str(round(resultado * 100, 2)) + ' %'
                incluidas += 1
                minFile = ('P%3d_mini_%4d.jpg' %
                           ((resultado * 100), incluidas)).replace(' ', '0')
                reporte.append({
                    'id': incluidas,
                    'file_path': img_path,
                    'score': float(round(resultado, 4)),
                    'miniature': minFile if createMin else ''
                })
            else:
                msg = 'Excluido por Score! '
                excluidos += 1
        except(OSError, ValueError):
            errores = errores + 1
            msg = 'No imagen valida!'
            continue
        finally:
            msg = msg + '\t' + img_path
            pbar.write(msg)
    print('\nTotal Archivos: ', nroArchivo)
    print('Total Archivos invalidos: ', errores)
    print('Total Imagenes Analizadas: ', nroArchivo - errores)
    print('Total Inagenes Incluidas en Reporte: ', incluidas)
    if(score > 0):
        print('Total Inagenes Excluidas por Score: ', excluidos)

    if(len(reporte)):
        print('\nGuardando Reporte...')
        outFile = str(path.join(outFolder, 'reporte.json'))
        with open(outFile, 'w') as f:
            json.dump(reporte, f)
        print('Reporte Guardado en ', path.abspath(outFile))

        if createMin:
            print('\nCreando miniaturas...')
            pbar = tqdm(reporte, total=len(reporte), unit=' imgs')
            for i in pbar:
                img = image.load_img(i['file_path'], target_size=(80, 80))
                file = path.abspath((path.join(outFolder, i['miniature'])))
                img.save(open(file, 'w'))

            print('Miniaturas creadas en ', path.abspath(outFolder))


if (__name__ == '__main__'):

    tiempo_inicial = time()
    parser = argparse.ArgumentParser(
        description='Calcula la probabilidad de que imagenes sean pornograficas.')
    parser.add_argument('ruta', metavar='path',
                        help='"Imagen" o Directorio a testear.')
    parser.add_argument('-o', '--out-folder', type=str,
                        help='Path al directorio de salida para reportes. Por defecto el directorio actual.')
    parser.add_argument('-s', '--score', type=float,
                        help='Minima Probabilidad (entre 0 y 1). Se excluiran los que esten por debajo. ')
    parser.add_argument('-m', '--miniature', action='store_true',
                        help='Crear miniaturas en el directorio de salida.')

    args = parser.parse_args()

    ruta = args.ruta
    if(args.miniature):
        createMin = True
    if(args.out_folder and path.isdir(args.out_folder)):
        outFolder = args.out_folder
    else:
        print('Parametro --out-folder no valido!')
    if(args.score):
        val = float(args.score)
        if((val >= 0) and (val <= 1)):
            score = val
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
