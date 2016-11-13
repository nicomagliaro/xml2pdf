#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Autor: Nicolas Magliaro  -- mailto: nicolasmagliaro@gmail.com
# Creacion: 22/4/2015                Revision: 06/11/2016
# Version: 0.1.0
"""
from optparse import OptionParser
import datetime
import os
import sys
import shutil
import base64, codecs
from xml.parsers.expat import ExpatError
import logging

# -------------------- SETTING GLOBALS ---------------------------------

# Datetime

datetime = datetime.date.today()

# File name list
toDelete = []
noParsed = []
# Basedir
try:
    Basedir = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    Basedir = os.path.dirname(os.path.abspath(sys.argv[0]))

# ------------------------ LOGGER CONFIG ------------------------------

# Setting
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler(os.path.join(Basedir, 'decoder.log'))
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)
logger.info('__Basedir__: Definiendo directorio del proyecto: %s' % Basedir)
logger.info('__Basedir__: Definiendo directorio del proyecto: %s' % Basedir)


# ----------------------------------------------------------------------

def header():
    print
    print '###################################################################################'
    print '############################   EXCEM TECHNOLOGY  ##################################'
    print '###################################################################################'
    print '###########    XML to PDF encoder    ## Date:  ' + str(datetime) + '  ########################'
    print '###################################################################################'
    print


logger.info(header())


def check_directory(output, dump):
    logger.info('__check_directory__: Verificando que existe la ruta (%s y %s)' % (output, dump))
    if not os.path.exists(output):
        logger.warning('__check_directory__: La ruta %s no estiste y sera creada' % output)
        try:
            os.makedirs(output)
            logger.info('__check_directory__: Ruta creada exitosamente')
        except Exception as error:
            logger.error('__check_directory__: ERROR: imposible crear directorio ' + repr(error))
            return False
    if not os.path.exists(dump):
        logger.warning('__check_directory__: La ruta %s no estiste y sera creada' % dump)
        try:
            os.makedirs(dump)
            logger.info('__check_directory__: Ruta creada exitosamente')
        except Exception as error:
            logger.error('__check_directory__: ERROR: imposible crear directorio ' + repr(error))
            return False
    logger.info('__check_directory__: Ruta verificada, son utilizables: (%s y %s)' % (output, dump))
    return True


def parse_options():
    HELP = ("\n"
            "		Decoder EXE can me executer either as Scheduled Task od from CMD:\n"
            "				1) Use the file 'config.cfg by set the parameter with -c {arg}' for Scheduled Task Mode\n"
            "					2) Run from command line otherwise.\n"
            "					3) Provide input PDF encoding with option -E.\n"
            "		")

    parser = OptionParser(usage='usage: { $python %prog [OPTIONS] HEX|BASE64|AUTO}',
                          version='%prog 0.1.0', description=HELP)

    parser.add_option('-i', '--input', action='store', type='string', dest='input',
                      help='Define the folder where xml files are stored')
    parser.add_option('-o', '--output', action='store', type='string', dest='output',
                      help='Define the folder where PDF are stored')
    parser.add_option('-d', '--dump', action='store', type='string', dest='dump',
                      help='Define the folder where parsed files are stored')

    options, args = parser.parse_args()

    logger.debug('__parse_options__: Inicializando lista de optiones: %s' % options)
    logger.debug('__parse_options__: Inicializando lista de argumentos: %s' % args)

    if len(args) > 1:
        parser.error('__parse_options__: No esta permitido mas de un argumento %s' % args)
        logger.warning('__parse_options__: Mas de un argumento ingresado %s' % args)

    if args == None:
        parser.print_usage()
        parser.error('__parse_options__: Enter format mode HEX|BASE64|AUTO')
        logger.warning('__parse_options__: No se ha definido el formato a decofificar')
        pass

    if options.input == None:
        parser.print_usage()
        parser.error('This option is required (-i) in command line mode.')
        logger.warning('__parse_options__: Hubo un error en los argumentos seleccionados: %s' % parser.parse_args())
        logger.info('__parse_options__: This option is required (-i) in command line mode.')
        return False

    if options.output == None:
        logger.info(
            '__parse_options__: No se ha definido una ruta donde guardar los PDF procesados. Definiendo %s/output' % Basedir)
        options.output = Basedir + '/output'

    if options.dump == None:
        logger.info(
            '__parse_options__: No se ha definido una ruta donde guardar los archivos procesados. Definiendo %s/decoded_files' % Basedir)
        options.dump = Basedir + '/decoded_files'

    if not os.path.exists(options.input):
        parser.error('La ruta ( %s ) especificada no existe' % options.input)
        logger.error('__parse_options__: La ruta ( %s ) especificada no existe' % options.input)

    opt = dict(input=options.input, output=options.output, dump=options.dump, format=args[0])

    # Verificando estructura de Carpetas del pryecto
    verify_folders = check_directory(opt['output'], opt['dump'])

    if not verify_folders:
        raise Exception('Ha ocurrido un problema!!!')
        logger.error('__parse_options__: Hubo un problema y no se pudo crear la estructura de directorios')

    logger.info('__parse_options__: Lista de configuración: %s' % opt)
    logger.debug('__parse_options__: Lista de opciones: %s' % opt)
    return opt


class decodePDF(object):
    def __init__(self, opt):
        self.params = opt
        self.file = ''
        self.date = str(datetime.strftime("%d-%m-%Y"))
        self.counter = 1001

    def __checkFiles(self):

        logger.debug('__CheckFiles__: decodePDF() va a iterar sobre la lista %s' % self.params)
        try:
            logger.debug('__CheckFiles__: Listando archivos en carpeta %s' % os.listdir(self.params['input']))
            for f in os.listdir(self.params['input']):
                self.file = os.path.join(self.params['input'], f)
                try:
                    logger.info('__CheckFiles__: Parseando archivo %s' % f)

                    self.__parseFile(self.file, self.params['output'], self.params['dump'])

                    logger.info('__CheckFiles__: Archivo decodificado')
                except:
                    logger.warning('__CheckFiles__: Este archivo ==> %s no pudo ser procesado' % f)
                    pass

            logger.info('__CheckFiles__: Lista de archivos no procesados %s' % noParsed)
            return True

        except:
            raise Exception('Ha ocurrido un error inesperado')
            logger.error('__CheckFiles__: Ha ocurrido un error inesperado', exc_info=True)
            return False

    def __decodeHexa(self, file):
        # inicializando Codecs
        decode_hex = codecs.getdecoder("hex_codec")

        with open(file, 'r') as f:
            # I already have file open at this point.. now what?
            opened_file = f.read()
            first_char = opened_file[0:2]  # get the first character

            if first_char == '':
                logger.warning('__decodeHEXA__: El archivo %s esta vacio y no puede ser procesado' % file)
                return False
            elif not first_char == '0x':
                logger.warning('__decodeHEXA__: El archivo %s no es Hexa y no puede ser procesado' % file)
                return False
            else:
                logger.debug('__decodeHEXA__: Decodificando HEXA: %s' % opened_file[2:])
                decoded_string = decode_hex(opened_file[2:])[0]
                logger.debug('__decodeHEXA__: Retornando decoded completado')

            f.close()

        return decoded_string

    def __parseFile(self, file, dst_dir, dump):
        """
        Decode PDF
        """
        pdf_hex = ''

        if os.path.isfile(file):

            logger.info('__parseFile__: leyendo %s' % file)
            # Parseando Archivo
            head, tail = os.path.split(file)
            filename = os.path.splitext(tail)[0]

            try:
                logger.info('__parseFile__: Preparando el archivo %s' % file)
                if self.__decodeHexa(file):
                    pdf_hex = base64.decodestring(self.__decodeHexa(file))
                    logger.debug('__parseFile__: El archivo %s se decodifico exitosamente' % filename)

                    self.counter += 1

                    logger.debug('__parseFile__: Valor de counter: %s' % str(self.counter))

                    file_b = dst_dir + '/' + str(filename) + '_' + self.date + '-' + str(self.counter) + '.pdf'
                    logger.info('__parseFile__: Creando archivo %s en memoria' % file_b)

                    with open(file_b, 'wb') as f_out:

                        logger.debug('__parseFile__: Se abrio el archivo %s en memoria' % str(f_out))
                        # Extrae el PDF en el directorio destino
                        f_out.write(pdf_hex)
                        logger.debug('__parseFile__: Volcado de memoria en %s' % str(f_out))
                        f_out.close()
                        logger.debug('__parseFile__: Cerrando archivo pdf')

                    # logger.info('__parseFile__: Archivo %s procesado' + ' PDF ==>: %s'%(file,str(filename)))

                    # Copia del archivo procesado al directorio de destino
                    shutil.copy(file, dump)
                    logger.info('__parseFile__: El archivo %s se ha copiado en %s' % (file, dump))
                    toDelete.append(str(file))
                    logger.debug('__parseFile__: Lista de archivos para borrar: %s' % toDelete)
                else:
                    logger.warning('__parseFile__: El archivo %s no se pudo decodificar' % filename)
            except:
                noParsed.append(file)
                logger.warning('__parseFile__: Este archivo ==> %s no tiene el formato adecuado' % file)
                logger.debug('Agregando archivo a lista de no procesados: %s' % noParsed)

        else:
            logger.warning('__parseFile__: %s no es un archivo' % file)
            return 0
        return True

    def __delFileInList(self, file_list):
        """
        Delete all parsed XML in List
        """
        logger.warning('__delFileInList__: Preparando para borrar la lista de archivos: %s' % toDelete)
        for f in os.listdir(self.params['input']):
            f = os.path.join(self.params['input'], f)
            if f in file_list:
                logger.info('__delFileInList__: Borrando ==> ' + f + ' de la carpeta ' + self.params['input'])
                os.remove(f)
                logger.warning('__delFileInList__: %s: El archivo ha sido eliminado de %s' % (f, self.params['input']))
                logger.info('__delFileInList__: Archivo eliminado exitosamente')
            else:
                logger.warning('__delFileInList__: %s: El archivo no ha podido ser eliminado' % f)
        return 0

    def getDecoded(self):
        try:
            self.__checkFiles()
            self.__delFileInList(toDelete)
            return 0
        except Exception, err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            logger.error('__getDecoded__: ERROR: %s\n' % str(err))
            return 1


def run():
    logger.debug('__run__: Analizando opciones ingresadas')
    options = parse_options()
    decode = decodePDF(options)
    decode.getDecoded()


if __name__ == "__main__":
    logger.info('__main__: Iniciando ejecución', exc_info=True)
    sys.exit(run())
