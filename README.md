Registro de Postulaciones en LinkedIn con Notion
Buscar empleo en LinkedIn puede ser un proceso abrumador, con múltiples postulaciones y seguimientos que realizar. 
Con esta herramienta, puedes llevar un registro organizado 
y detallado de todas las ofertas a las que aplicas directamente en Notion, 
facilitando el seguimiento de cada oportunidad.

Ventajas de usar esta herramienta:
✅ Organización Centralizada: Guarda automáticamente los detalles de cada oferta en una base de datos de Notion, evitando la pérdida de información.

✅ Seguimiento Eficiente: Registra la empresa, puesto, descripción y fecha de postulación, lo que te permite hacer un mejor seguimiento de tu proceso de selección.

✅ Automatización y Ahorro de Tiempo: En lugar de copiar y pegar datos manualmente, la herramienta extrae automáticamente la información relevante de la oferta de LinkedIn.

✅ Accesible desde Cualquier Dispositivo: Al estar en Notion, puedes revisar y actualizar tu registro desde cualquier lugar, ya sea en tu computadora o en tu móvil.

✅ Toma de Decisiones Inteligente: Analiza las ofertas en las que has postulado y optimiza tu estrategia de búsqueda de empleo.

¿Por qué usarlo?
Si aplicas a muchas ofertas en LinkedIn, llevar un control manual puede ser tedioso y poco eficiente. Con esta herramienta, 
te aseguras de que cada postulación queda registrada con todos los datos importantes, lo que te ayuda a gestionar 
mejor tu búsqueda de empleo y aumentar tus oportunidades de éxito.


![image](https://github.com/user-attachments/assets/52240440-b29b-4bc6-ade1-3b21cb9b04c6)

![image](https://github.com/user-attachments/assets/a03f9209-6996-4dfd-a6da-525e0dca7ddd)

![image](https://github.com/user-attachments/assets/53c0a9ef-5904-4963-96ce-65b35e7aa488)

![image](https://github.com/user-attachments/assets/62767892-a1fc-4bff-91d9-db063d539372)

![image](https://github.com/user-attachments/assets/9f2a52b1-3679-4d8e-ac55-2e9e3fc55220)





# Capítulo 1: Generación del Ejecutable (.exe)

## Introducción

Este capítulo describe el proceso para convertir la aplicación Python en un archivo ejecutable de Windows (`.exe`) utilizando PyInstaller. El objetivo es distribuir la aplicación sin necesidad de que el usuario tenga Python instalado en su equipo.

---

## Requisitos Previos

Antes de generar el ejecutable, asegúrese de cumplir con los siguientes requisitos:

* Python 3.12 o superior instalado.
* Entorno virtual configurado (`.venv`).
* Todas las dependencias instaladas desde `requirements.txt`.
* Archivo principal de la aplicación: `Notion3.py`.
* Archivo de icono: `favicon.ico`.

---

## Activar el Entorno Virtual

Abra una terminal PowerShell en la carpeta del proyecto y ejecute:

```powershell
.venv\Scripts\Activate.ps1
```

Si la activación fue exitosa, el prompt mostrará:

```powershell
(.venv) PS C:\Ruta\Del\Proyecto>
```

---

## Instalar PyInstaller

Si PyInstaller no está instalado, ejecute:

```powershell
pip install pyinstaller
```

Verifique la instalación:

```powershell
pyinstaller --version
```

---

## Limpiar Compilaciones Anteriores

Antes de generar una nueva versión, elimine los archivos temporales de compilaciones previas:

```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
```

Esto evita conflictos con configuraciones antiguas.

---

## Generar el Ejecutable

Ejecute el siguiente comando:

```powershell
pyinstaller --onefile --windowed --clean --icon=favicon.ico --name=Notlink Notion3.py
```

### Explicación de Parámetros

| Parámetro            | Descripción                                              |
| -------------------- | -------------------------------------------------------- |
| `--onefile`          | Genera un único archivo ejecutable.                      |
| `--windowed`         | Oculta la consola de comandos al ejecutar la aplicación. |
| `--clean`            | Elimina archivos temporales de compilaciones anteriores. |
| `--icon=favicon.ico` | Asigna el icono personalizado al ejecutable.             |
| `--name=Notlink`     | Define el nombre final del archivo ejecutable.           |
| `Notion3.py`         | Archivo principal de la aplicación.                      |

---

## Resultado de la Compilación

Al finalizar el proceso, PyInstaller mostrará un mensaje similar a:

```text
Build complete! The results are available in: dist
```

El ejecutable generado se encontrará en:

```text
dist\Notlink.exe
```

---

## Estructura Generada

```text
build/
dist/
└── Notlink.exe
Notlink.spec
```

### Descripción

* `build/`: archivos temporales utilizados durante la compilación.
* `dist/`: contiene el ejecutable final.
* `Notlink.spec`: archivo de configuración generado por PyInstaller.

---

## Problema Común: Icono Antiguo

Windows puede almacenar iconos en caché. Si el ejecutable muestra un icono anterior:

1. Elimine las carpetas `build` y `dist`.
2. Elimine el archivo `.spec`.
3. Reinicie el Explorador de Windows o el equipo.
4. Compile nuevamente.

Si el problema persiste, genere temporalmente el ejecutable con otro nombre:

```powershell
pyinstaller --onefile --windowed --clean --icon=favicon.ico --name=NotlinkV2 Notion3.py
```

Esto obliga a Windows a reconstruir la caché de iconos.

---

## Verificación Final

Después de la compilación:

1. Abra la carpeta `dist`.
2. Ejecute `Notlink.exe`.
3. Verifique que:

   * El icono sea el correcto.
   * La ventana de la aplicación se abra correctamente.
   * La conexión con Notion funcione.
   * La integración con Groq procese correctamente las ofertas laborales.

Una vez completadas estas verificaciones, la aplicación está lista para distribución.



## 2. Configuración de Credenciales

Antes de utilizar la aplicación, es necesario configurar las credenciales de acceso para Notion y Groq.

### 2.1 Obtener la API Key de Groq

1. Accede al panel de Groq.
2. Dirígete a **API Keys**.
3. Selecciona **Create API Key**.
4. Copia la clave generada.

Ejemplo:

```text
gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.2 Obtener el Token de Notion

1. Accede al portal de desarrolladores de Notion.
2. Crea una nueva conexión o utiliza una existente.
3. Copia el **Access Token** generado.

Ejemplo:

```text
ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.3 Obtener el Database ID

1. Abre tu base de datos en Notion.
2. Selecciona **Abrir como página**.
3. Copia la URL de la base de datos.

Ejemplo:

```text
https://app.notion.com/p/1927803780f880689fb6c59ee4469e13?v=1927803780f8804abbda000c7e50610f
```

El **Database ID** corresponde a la primera cadena de caracteres:

```text
1927803780f880689fb6c59ee4469e13
```

### 2.4 Compartir la Base de Datos

La integración de Notion debe tener acceso a la base de datos:

1. Abre la base de datos.
2. Haz clic en **Compartir**.
3. Selecciona **Invitar conexión**.
4. Elige la integración creada.
5. Confirma los permisos.

### 2.5 Configuración en la Aplicación

Introduce los siguientes valores en la ventana de configuración:

| Campo              | Valor                       |
| ------------------ | --------------------------- |
| Notion API Key     | Token de Notion (`ntn_...`) |
| Notion Database ID | ID de la base de datos      |
| Groq API Key       | Clave de Groq (`gsk_...`)   |

Finalmente, haz clic en **Guardar** para almacenar la configuración.
