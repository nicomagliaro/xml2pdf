Instrucciones de uso:

Estructura del paquete
./
    ./Pdf_decoder
		- config.cfg   // archivo con las rutas relativas y el nombre de las etiquetas donde se guarda el PDF codificado a Base64
	    - xml2pdf.cmd  // autoejecutable de la aplicacion
	    - xml2pdf.exe // Programa compilado
		- Logs 
			- dump.txt // Log historico de archivos precesados
		- input // XML's a precesar
		- output // PDF's precesados
		- xml // XML's precesados exitosamente

El programa se puede usar desde la linea de comandos:
		ejecutar xml2pdf.exe --help para ver todas las opciones aceptadas
		
El programa puede ejecutarse desde el archivo batch xml2pdf.cmd manualmente o a traves de una Tarea Programada
Esta es la unica opcion de deja un Logs de los archivos procesados
1) Rellenar el parametro de Input en el fichero config.cfg, los parametros de output y xml se pueden crear o sino son creados en el Path por defecto
2) Ejecutar el archivo ./Pdf_decoder/xml2pdf.cmd desde un CMD o con doble click
3) Los PDF se procesan a la carpeta ./output
4) Una vez procesados, los xml se copian a la carpeta ./xml

