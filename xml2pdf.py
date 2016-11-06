#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Autor: Nicolas Magliaro  -- mailto: nicolasmagliaro@gmail.com
# Creacion: 22/4/2015                Revision: 06/11/2016
# Version: 0.2.2
"""

from ConfigParser import SafeConfigParser
from optparse import OptionParser
import base64, shutil, os, sys, datetime
import xml.dom.minidom as minidom
from xml.parsers.expat import ExpatError

# -------------------- SETTING GLOBALS ---------------------------------

# Datetime

datetime = str(datetime.date.today())

# File name list
toDelete = []
noParsed = []

# Basedir
try:
    Basedir = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    Basedir = os.path.dirname(os.path.abspath(sys.argv[0]))


# ----------------------------------------------------------------------

def check_directory(output, xml):
    if not os.path.exists(output):
        try:
            os.makedirs(output)
        except Exception as error:
            print('ERROR: imposible crear directorio ' + repr(error))
            return False
    if not os.path.exists(xml):
        try:
            os.makedirs(xml)
        except Exception as error:
            print('ERROR: imposible crear directorio ' + repr(error))
            return False

    return True


def parse_options():
    HELP = ("\n"
            "		This program has 2 way to run it:\n"
            "				1) Use the file 'config.cfg to set the parameter with -c {arg}'.\n"
            "					2) Run from command line otherwise.\n"
            "		")

    parser = OptionParser(usage='usage: FILE MODE: { $python %prog -c } or CMD MODE: { $python %prog [OPTIONS] }',
                          version='%prog 0.2.2', description=HELP)
    parser.add_option('-c', '--config', action="store_true", dest="config", default=False,
                      help='This option force to read from config.cfg file for non CMD Mode. Take no argument')
    parser.add_option('-i', '--input', action='store', type='string', dest='input',
                      help='Define the folder where xml files are stored')
    parser.add_option('-o', '--output', action='store', type='string', dest='output',
                      default=os.path.join(Basedir, 'output'),
                      help='Define the folder to store PDF converted')
    parser.add_option('-d', '--dump', action='store', type='string', dest='xml', default=os.path.join(Basedir, 'xml'),
                      help='Define destination folder for parsed XMLs')
    parser.add_option('-n', '--tagname', action='store', type='string', dest='w_name',
                      help='Specify the tag name to parse PDF strings')
    parser.add_option('-t', '--tag_content', action='store', type='string', dest='content',
                      help='Specify the tag where is B64 PDF to convert')

    options, args = parser.parse_args()

    if (not options.config and options.input == None and options.w_name == None and options.content == None):

        parser.print_usage()
        raise Exception('Debe seleccionar al menos una opción válida')
        return False

    else:
        if options.config:
            opt = {
                'config': True,
                'input': '',
                'output': '',
                'xml': '',
                'w_name': '',
                'w_cont': '',
            }
            return opt
        else:
            if not os.path.exists(options.input):
                parser.error('La ruta ( %s ) especificada no existe' % options.input)

            if options.input is None:
                parser.error('This option is required (-i) in command line mode.')

            if options.w_name is None:
                parser.error('This option is required (-n) in command line mode.')

            if options.content is None:
                parser.error('This option is required (-t) in command line mode.')

            opt = {
                'config': False,
                'input': options.input,
                'output': options.output,
                'xml': options.xml,
                'w_name': options.w_name,
                'w_cont': options.content,
            }

            verify_folders = check_directory(opt['output'], opt['xml'])
            if not verify_folders:
                raise Exception('Ha ocurrido un problema!!!')

            return opt


# ___________________________________________________________________

def Mode():
    mode = parse_options()
    opt = {}
    if mode:
        if mode['config']:
            # Config params set in config.cfg
            config = SafeConfigParser()
            config_path = os.path.join(Basedir, 'config.cfg')
            if os.path.isfile(config_path):
                config.read(config_path)
            elif config.read('config.cfg'):
                config.read('config.cfg')
            else:
                raise Exception('Cannot find config.cfg. Make sure it exists')

            # Parameter config.cfg
            input_dir = config.get('ruta', 'input')
            output_dir = config.get('ruta', 'pdf_output')
            dst_dir = config.get('ruta', 'xml_output')
            w_name = config.get('ruta', 'warrant_name')
            w_cont = config.get('ruta', 'container_name')

            opt = {
                'input': input_dir,
                'output': output_dir,
                'xml': dst_dir,
                'w_name': w_name,
                'w_cont': w_cont,
            }
            if not os.path.exists(opt['input']):
                raise Exception('La ruta (%s) especificada no existe' % opt['input'])

            verify_folders = check_directory(opt['output'], opt['xml'])
            if not verify_folders:
                raise Exception('Ha ocurrido un problema!!!')
        else:

            input_dir = mode['input']
            output_dir = mode['output']
            dst_dir = mode['xml']
            w_name = mode['w_name']
            w_cont = mode['w_cont']

            opt = {
                'input': input_dir,
                'output': output_dir,
                'xml': dst_dir,
                'w_name': w_name,
                'w_cont': w_cont,
            }

        return opt
    else:
        return False


def Main():
    try:
        CheckFiles('xml')
        Del_File_In_List(toDelete)
        return 0
    except Exception, err:
        sys.stderr.write('ERROR: %s\n' % str(err))
        return 1


def CheckFiles(ext):
    """
	Iterate all XML in destination
	"""
    Header()
    params = Mode()
    if params:
        for file in os.listdir(params['input']):
            if file.endswith('.%s' % ext):
                xml = os.path.join(params['input'], file)
                try:
                    parseFile(params['output'], xml, params['xml'], params['w_name'], params['w_cont'])
                except:
                    print
                    print('Este archivo ==>' + xml + ' no tiene el formato adecuado')
                    pass
    else:
        raise Exception('Ha ocurrido un error inesperado')
        return False


def parseFile(path, xml, dst_dir, w_name, w_cont):
    """
	Decode PDF found in xml
	"""
    doc = ''
    try:
        doc = minidom.parse(xml)
        # Parseando el XML
        node = doc.documentElement
        names = doc.getElementsByTagName(w_name)[0].firstChild.data
        pdf = doc.getElementsByTagName(w_cont)[0].firstChild.data
        f_out = open(path + '/' + str(names), 'wb')

        # Decodifica de Base64 a Hex
        pdf_hex = base64.decodestring(pdf)

        # Extrae el PDF en el directorio destino
        f_out.write(pdf_hex)
        f_out.close()
        print
        print('Archivo ' + xml + ' procesado' + ' PDF ==>: ' + str(names))

        # Copia el xml procesado al directorio de destino
        shutil.copy(xml, dst_dir)
        toDelete.append(str(xml))

    except ExpatError:
        # not sure how you want to handle the error... so just passing back as string
        noParsed.append(xml)
        print
        print('Este archivo ==>' + xml + ' no tiene el formato adecuado')
    return 0


def Del_File_In_List(file_list):
    """
		Delete all parsed XML in List
	"""
    params = Mode()
    for f in os.listdir(params['input']):
        f = os.path.join(params['input'], f)
        if f in file_list:
            print 'Borrando==> ' + f + ' de la carpeta ' + params['input']
            os.remove(f)
            print
        else:
            print
    return 0


def Header():
    print
    print '###################################################################################'
    print '############################   EXCEM TECHNOLOGY  ##################################'
    print '###################################################################################'
    print '###########    XML to PDF encoder    ## Date:  ' + datetime + '  ########################'
    print '###################################################################################'
    print


if __name__ == "__main__":
    sys.exit(Main())