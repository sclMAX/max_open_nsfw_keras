from cx_Freeze import setup, Executable

setup(
    name = 'Max Open Nsfw',
    version = '1.0',
    description = 'Calcula la probabilidad de que imagenes sean pornograficas.',
    executables = [Executable('max_open_nsfw.py')],
)