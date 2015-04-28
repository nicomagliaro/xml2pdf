"""
# Autor: Nicolas Magliaro  -- mailto: nicolasmagliaro@gmail.com
# Creacion: 22/4/2015                Revision: 28/4/2015
# Version: 0.1.4
"""
from ConfigParser import SafeConfigParser
import base64, shutil, os, sys, datetime
import xml.dom.minidom as minidom
from xml.parsers.expat import ExpatError

#___________________________________________________________________

#Config params set in config.cfg
config = SafeConfigParser()
CONFIG = os.path.join(os.path.dirname(__file__), 'config.cfg')
config.read(CONFIG)

#Parameter config.cfg

today = str(datetime.date.today())
input_dir = config.get('ruta', 'input')
output_dir = config.get('ruta','pdf_output')
dst_dir = config.get('ruta','xml_output')
w_name = config.get('ruta', 'warrant_name')
w_cont = config.get('ruta','container_name')

#----------------------------------------------------------------------

#File name list
toDelete = []
noParsed = []

def Main():
    try:
        CheckFiles(str(input_dir), 'xml')
        Del_File_In_List(toDelete)
        return 0
    except Exception, err:
        sys.stderr.write('ERROR: %s\n' % str(err))
        return 1

def CheckFiles(dir, ext):
    """
    Iterate all XML in destination
    """
    Header()
    for file in os.listdir(dir):
        if file.endswith('.%s' % ext):
            xml = os.path.join(dir, file)
            parseFile(output_dir, xml)

def parseFile(path, xml):
    """
    Decode PDF found in xml
    """
    doc = ''
    try:
        doc = minidom.parse(xml)
        #Parseando el XML
        node = doc.documentElement
        names = doc.getElementsByTagName(w_name)[0].firstChild.data
        pdf = doc.getElementsByTagName(w_cont)[0].firstChild.data
        f_out = open(path+'/'+str(names), 'wb')

        # Decodifica de Base64 a Hex
        pdf_hex = base64.decodestring(pdf)

        # Extrae el PDF en el directorio destino
        f_out.write(pdf_hex)
        f_out.close()
        print
        print('Archivo '+xml+' procesado'+' PDF ==>: '+ str(names))

        # Copia el xml procesado al directorio de destino
        shutil.copy(xml,dst_dir)
        toDelete.append(str(xml))

    except ExpatError:
        # not sure how you want to handle the error... so just passing back as string
        noParsed.append(xml)
        print
        print('Este archivo ==>'+xml+' no pudo ser procesado!!!')
    return 0

def Del_File_In_List(file_list):
    """
        Delete all parsed XML in List
    """
    for f in os.listdir(input_dir):
        f = os.path.join(input_dir, f)
        if f in file_list:
            print 'Borrando==> '+f+' de la carpeta '+input_dir
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
    print '##########################    XML to PDF encoder    ## Date:  '+ today +'  #########'
    print '###################################################################################'
    print

if __name__ == "__main__":
    sys.exit(Main())
