# max_open_nsfw_keras

Conversion de Yahoo/onpen_nsfw caffe model a Keras Tensorflow model.

Requerimientos:

  - Python 3.6
  
Instalacion:

  - git clone https://github.com/sclMAX/max_open_nsfw_keras.git
  - cd max_open_nsfw_keras
  - pip install -r requisitos.txt # para instalar las dependencias

Uso:

  - python max_open_nsfw.py  [Directorio a escanear]

Crear .exe:

  - pip3 install cx_freeze
  - python3 make_exe.py build
  - creara una carpeta "build" dentro de la cual estara el .exe 
  - copiar los archivos del modelo keras (max_open_nsfw.json y .h5) al directorio donde se encuntra el .exe