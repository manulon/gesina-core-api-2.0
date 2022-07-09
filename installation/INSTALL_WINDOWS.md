# Windows HECRAS with celery 

*Español*

Desde Linux o macOS:
1) Instalar manualmente Vagrant y VirtualBox.
2) Abrir la consola en la carpeta raíz de este proyecto.
3) Ejecutar `vagrant up`. Esto tarda un rato, dado que crea la máquina virtual con Windows. Más información en el Vagrantfile.
   1) Al finalizar, se debe abrir VirtualBox para ingresar a Windows.
   2) Verificar que Windows esté en idioma Inglés, ya que HECRAS lo requiere por la configuración de decimales.

Con esto, tenemos instalado el ambiente virtual para ejecutar Windows. 

Una vez funcionando lo anterior, acceder a Windows.

#### HECRAS
Desde Windows:
- Descargar el instalador de HECRAS 5.0.7 desde la página oficial. Ejecutar instalador
- Una vez instalado, abrirlo manualmente una primera vez para aceptar los términos y condiciones.

#### Python 
Desde Windows:
- Instalar python 3.10.5 (descargado de python.org)
    - Instalar PIP
        - Abrir Powershell (consola) y ejecutar `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`. Esto nos descarga un archivo que es el instalador de PIP.
        - Para ejecutar el instalador, parados en la misma carpeta del instalador `get-pip.py` ejecutar `python get-pip.py`.
    - Instalar pipenv. Una vez instalado pip, ejecutar `pip install pipenv`.
- Instalación de aplicación GESINA
  - Desde powershell, navegar hasta la carpeta `C://gesina-core-api` y ejecutar `pipenv install`. Con eso instalamos la aplicación en Windows.
  - Terminada la instalación, abrir el archivo ubicado en `gesina-core-api/installation/run_in_windows.ps1`, copiarse el codigo y llevarlo a la powershell y ejecutarlo. 

Con eso, dejamos funcionando el servidor del lado de Windows. 
Esta parte de la aplicación quedará atento a eventos que le indiquen la ejecución de simulaciones en HECRAS.


### Vagrant hint
En caso de necesitar usar los servicios del host desde la máquina virtual de Vagrant, se puede acceder a través de la ip 10.0.2.2
