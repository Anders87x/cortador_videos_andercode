# 🎬 Cortador de Videos AnderCode

Herramienta web local para convertir videos largos de cursos en clips listos para **Reels, TikTok y Shorts**.

El proyecto está construido con **Python + Flask + FFmpeg/FFprobe** y fue pensado para un flujo de trabajo real: cargar un video largo, analizarlo, revisar los cortes, seleccionar únicamente los fragmentos útiles y generar versiones verticales 9:16 con branding, hook inicial y outro promocional.

> 🔒 Todo el procesamiento se realiza de forma local en tu PC.  
> Los videos no se suben a servicios externos.

---

## ✨ ¿Qué resuelve este proyecto?

Un video largo puede convertirse en varios clips cortos de forma repetible y controlada:

```text
Video largo
   ↓
Eliminar intro
   ↓
Dividir en clips
   ↓
Preview
   ↓
Seleccionar clips
   ↓
Hook opcional
   ↓
Reel 9:16
   ↓
Branding
   ↓
Outro opcional
   ↓
CPU / NVIDIA GPU
   ↓
MP4 final
```

Ejemplo:

```text
Hook:      0.5 s
Contenido: 30 s
Outro:      5 s
----------------
Total:    35.5 s
```

---

# 🚀 Funcionalidades de la V1

## 🎥 Videos

- Carga local de:
  - MP4
  - MOV
  - MKV
  - WEBM
  - AVI
- Límite actual por archivo: **8 GB**.
- Drag & drop o selector de archivos.
- Preview del video original desde el navegador.

---

## 🔍 Análisis con FFprobe

El backend utiliza **FFprobe** para detectar:

- duración;
- resolución;
- codec de video;
- FPS;
- presencia de audio;
- codec de audio.

Después calcula automáticamente los segmentos según:

- segundos de intro a eliminar;
- duración deseada de cada clip.

---

## ✂️ Cortes

- Intro configurable.
- Duración configurable.
- Último clip parcial soportado.
- Selección individual.
- Seleccionar todos.
- Deseleccionar todos.
- Preview de cada fragmento antes de generarlo.

---

## 📱 Reel vertical 9:16

El formato predeterminado de la V1 es:

```text
1080 × 1920
9:16
```

El video original se conserva completo.

Para llenar el espacio vertical se utiliza:

- video ampliado como fondo;
- desenfoque configurable;
- contenido principal centrado;
- escala configurable;
- posición:
  - arriba;
  - centro;
  - abajo.

Esto evita recortar presentaciones, código, Excel, navegadores u otros contenidos de cursos.

---

## 🎨 Branding AnderCode

El branding está activado por defecto.

Permite agregar:

- título superior;
- firma inferior;
- zona segura visual.

Firma predeterminada:

```text
anderson-bastidas.com
```

El tamaño de la firma se adapta automáticamente a textos largos.

---

# ⚡ Hook inicial

Cada proyecto puede tener una imagen específica de gancho.

Configuración:

- PNG / JPG / JPEG / WEBP;
- máximo 10 MB;
- duración predeterminada: **0.5 s**;
- duración configurable entre **0.2 y 3 s**;
- silencio;
- fade opcional.

La misma imagen se utiliza en todos los clips generados del proyecto.

Ejemplo:

```text
HOOK
0.5 segundos
↓
CONTENIDO
30 segundos
```

---

# 📢 Outro promocional

Cada proyecto también puede tener una imagen promocional final.

Configuración:

- PNG / JPG / JPEG / WEBP;
- máximo 10 MB;
- duración predeterminada: **5 s**;
- duración configurable entre **2 y 10 s**;
- silencio;
- fade opcional.

Ejemplo:

```text
CONTENIDO
30 segundos
↓
PUBLICIDAD DEL CURSO
5 segundos
```

---

# 🔀 Render final

Cuando hook y outro están activos, FFmpeg genera:

```text
Hook
+
Clip
+
Outro
=
Un único MP4
```

El audio del clip se conserva.

Hook y outro usan audio silencioso para que la concatenación mantenga una estructura de audio válida.

---

# 🚄 Motor de render

La V1 tiene tres opciones.

## Auto · recomendado

```text
Auto
```

Comportamiento:

1. Detecta si FFmpeg incluye `h264_nvenc`.
2. Intenta utilizar NVIDIA NVENC.
3. Si NVENC falla por GPU o driver, vuelve automáticamente a CPU.
4. Si NVENC no está disponible, usa CPU directamente.

---

## NVIDIA NVENC · GPU

Fuerza:

```text
h264_nvenc
```

Ideal para procesar muchos Reels más rápido en una GPU NVIDIA compatible.

---

## CPU

Utiliza:

```text
libx264
```

Es el modo de máxima compatibilidad.

---

# ⛔ Cancelar procesamiento

Durante una generación aparece:

```text
Cancelar procesamiento
```

La cancelación es real.

El backend:

1. marca el trabajo como cancelado;
2. localiza el proceso FFmpeg activo;
3. intenta terminarlo;
4. si no responde, lo fuerza;
5. detiene la cola restante.

No es necesario cerrar Flask.

---

# ⏱️ Progreso de generación

Durante una tanda se muestra:

- clip actual;
- porcentaje;
- cantidad procesada;
- tiempo transcurrido;
- tiempo restante aproximado.

Ejemplo:

```text
Generando Reel 04
4 de 12 clips procesados
Transcurrido 01:42 · Restante aprox. 03:24
```

---

# 📁 Abrir carpeta de resultados

Después de generar un clip puedes utilizar:

```text
Abrir carpeta
```

En Windows se abrirá directamente el explorador en:

```text
outputs/<proyecto>/
```

También funciona al reabrir un proyecto reciente que ya tenga resultados.

---

# 💾 Proyectos recientes

Los proyectos se almacenan localmente sin base de datos.

Archivo:

```text
data/projects.json
```

Se conserva:

- nombre del video;
- archivo local;
- duración;
- intro;
- duración de clips;
- formato;
- escala;
- posición;
- blur;
- branding;
- título;
- firma;
- hook;
- imagen de hook;
- duración/fade del hook;
- outro;
- imagen de outro;
- duración/fade del outro.

Al volver a abrir Flask puedes retomar el proyecto sin volver a cargar el video.

---

# ⚙️ Presets

La V1 incluye:

### Reel AnderCode

```text
Intro:      5 s
Clip:       30 s
Formato:    Reel 9:16
Escala:     88%
Posición:   Centro
Blur:       25
Branding:   Sí
Firma:      anderson-bastidas.com
```

### Reel limpio

Reel vertical sin branding.

### Formato original

Mantiene la proporción original del video.

También puedes crear tus propios presets.

Los presets personalizados se guardan en:

```text
localStorage
```

del navegador.

---

# 🌗 Interfaz

El portal incluye:

- modo claro;
- modo oscuro;
- persistencia del tema;
- navegación por etapas;
- acordeones de configuración;
- diseño responsive;
- estado local;
- preview vertical;
- mensajes de éxito/error;
- detalle técnico de FFmpeg en caso de fallo.

---

# 🧾 Logs de render

Cada intento queda registrado en:

```text
data/render_logs.jsonl
```

Cada línea es un JSON independiente.

Ejemplo conceptual:

```json
{
  "timestamp": "2026-10-08T15:30:00+00:00",
  "status": "success",
  "project_id": "curso-demo-12345678",
  "clip_index": 4,
  "encoder_mode": "auto",
  "encoder_used": "NVIDIA NVENC",
  "hook_enabled": true,
  "outro_enabled": true
}
```

También se registran:

- errores;
- cancelaciones;
- detalle FFmpeg;
- archivo generado.

---

# 🧠 Arquitectura del proyecto

La aplicación está separada por responsabilidades.

```text
cortador_videos_andercode/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── routes/
│   └── video_routes.py
│
├── services/
│   ├── ffmpeg_service.py
│   ├── outro_service.py
│   ├── project_service.py
│   ├── render_log_service.py
│   ├── render_manager.py
│   ├── system_service.py
│   └── video_service.py
│
├── utils/
│   └── video_helpers.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       └── app.js
│
├── tests/
│   ├── test_ffmpeg_builders.py
│   ├── test_project_service.py
│   └── test_video_helpers.py
│
├── data/
│   ├── projects.json
│   ├── render_logs.jsonl
│   └── project_assets/
│
├── uploads/
│
└── outputs/
```

---

# 🧩 Responsabilidad de cada módulo

## `app.py`

Inicializa Flask:

- configuración;
- carpetas;
- Blueprint;
- servidor local.

---

## `config.py`

Configuración general:

- rutas;
- límites;
- formatos permitidos;
- directorios de datos.

---

## `routes/video_routes.py`

Endpoints HTTP.

Coordina:

- uploads;
- análisis;
- generación;
- proyectos;
- hook/outro;
- cancelación;
- motores;
- carpeta de salida.

---

## `services/video_service.py`

Lógica principal de negocio:

- validar video;
- analizar;
- validar segmentos;
- preparar configuración;
- generar clips.

---

## `services/ffmpeg_service.py`

Toda la integración multimedia:

- FFprobe;
- FFmpeg;
- filtros;
- 9:16;
- branding;
- hook;
- outro;
- audio;
- libx264;
- h264_nvenc;
- fallback GPU → CPU.

---

## `services/project_service.py`

Persistencia local de proyectos mediante JSON.

---

## `services/outro_service.py`

Gestiona los assets promocionales:

```text
hook.*
outro.*
```

---

## `services/render_manager.py`

Gestiona los procesos FFmpeg activos.

Permite cancelar un render en ejecución.

---

## `services/render_log_service.py`

Escribe:

```text
data/render_logs.jsonl
```

de manera segura entre threads.

---

## `services/system_service.py`

Permite abrir carpetas locales desde el portal.

---

## `utils/video_helpers.py`

Funciones auxiliares:

- formatos;
- segmentos;
- tiempos;
- archivos seguros.

---

# 🌐 Endpoints principales

| Método | Endpoint | Función |
|---|---|---|
| GET | `/` | Portal |
| POST | `/upload` | Cargar video |
| POST | `/analyze` | Analizar con FFprobe |
| POST | `/generate-clip` | Generar un clip |
| GET | `/render-capabilities` | Detectar NVENC |
| POST | `/render-jobs/<id>/cancel` | Cancelar render |
| POST | `/render-jobs/<id>/finish` | Cerrar job |
| GET | `/projects` | Proyectos recientes |
| GET | `/projects/<id>` | Obtener proyecto |
| DELETE | `/projects/<id>` | Eliminar proyecto |
| DELETE | `/projects` | Limpiar proyectos |
| POST | `/projects/<id>/open-output` | Abrir carpeta |
| GET/PATCH | `/projects/<id>/hook` | Configuración hook |
| POST/GET/DELETE | `/projects/<id>/hook-image` | Imagen hook |
| GET/PATCH | `/projects/<id>/outro` | Configuración outro |
| POST/GET/DELETE | `/projects/<id>/outro-image` | Imagen outro |
| GET | `/uploads/<archivo>` | Servir video local |
| GET | `/outputs/<proyecto>/<formato>/<archivo>` | Servir clip generado |

---

# 🛠️ Tecnologías utilizadas

## Backend

- Python
- Flask 3.1.3
- Werkzeug
- Jinja2

## Multimedia

- FFmpeg
- FFprobe
- H.264
- AAC
- libx264
- NVIDIA NVENC / h264_nvenc

## Frontend

- HTML5
- CSS3
- JavaScript Vanilla
- Fetch API
- LocalStorage
- HTML5 Video

## Persistencia

No se utiliza MySQL ni SQLite en la V1.

Se utilizan:

```text
JSON
JSONL
LocalStorage
filesystem local
```

---

# 📦 Dependencias Python

Actualmente:

```text
Flask==3.1.3
Werkzeug==3.1.9
Jinja2==3.1.6
MarkupSafe==3.0.4
itsdangerous==2.2.0
click==8.5.0
blinker==1.9.0
```

FFmpeg se instala a nivel del sistema y no mediante `pip`.

---

# 🖥️ Instalación inicial en Windows

Esta sección se realiza **una sola vez** en una PC nueva.

## 1. Clonar el repositorio

```bash
git clone https://github.com/Anders87x/cortador_videos_andercode.git
```

Entrar al proyecto:

```bash
cd cortador_videos_andercode
```

Cambiar a `develop` mientras la V1 siga en validación:

```bash
git switch develop
```

---

## 2. Crear el entorno virtual

```bash
python -m venv venv
```

---

## 3. Activar el entorno virtual

### CMD

```bash
venv\Scripts\activate
```

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea scripts temporalmente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

y luego:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 4. Actualizar pip

```bash
python -m pip install --upgrade pip
```

---

## 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 6. Instalar FFmpeg

FFmpeg debe estar instalado en Windows y disponible en el `PATH`.

Validar:

```bash
ffmpeg -version
```

y:

```bash
ffprobe -version
```

Si ambos comandos responden, la instalación multimedia está lista.

---

# ⚡ Validar NVIDIA NVENC

Ejecuta:

```bash
ffmpeg -hide_banner -encoders | findstr nvenc
```

Si aparece:

```text
h264_nvenc
```

tu build de FFmpeg incluye NVENC.

> Esto no garantiza que el driver/GPU puedan utilizarlo.  
> El modo **Auto** del portal controla ese caso y vuelve a CPU si es necesario.

---

# ▶️ COMANDOS PARA INICIAR EL PROYECTO CADA DÍA

Esta es la sección más importante para volver a trabajar rápidamente.

Supongamos que el proyecto está en:

```text
D:\Python_Dev\cortador-videos
```

## Opción recomendada — CMD

### 1. Abrir CMD

### 2. Entrar a la carpeta

```bat
cd /d D:\Python_Dev\cortador-videos
```

### 3. Actualizar la rama

```bat
git switch develop
git pull origin develop
```

### 4. Activar Python

```bat
venv\Scripts\activate
```

### 5. Iniciar Flask

```bat
python app.py
```

### 6. Abrir en el navegador

```text
http://127.0.0.1:5000
```

---

# 🚀 Inicio rápido diario

Una vez instalado todo, normalmente solo necesitarás:

```bat
cd /d D:\Python_Dev\cortador-videos
git switch develop
git pull origin develop
venv\Scripts\activate
python app.py
```

Después:

```text
http://127.0.0.1:5000
```

---

# 🟢 Cuando la V1 pase a main

Después del merge final, el inicio diario podrá ser:

```bat
cd /d D:\Python_Dev\cortador-videos
git switch main
git pull origin main
venv\Scripts\activate
python app.py
```

---

# 🛑 Cómo detener el servidor

En la terminal donde corre Flask:

```text
Ctrl + C
```

Después puedes cerrar CMD.

---

# 🔄 Si cambió requirements.txt

Después de un `git pull`, si se añadieron dependencias:

```bat
venv\Scripts\activate
pip install -r requirements.txt
```

No necesitas recrear el entorno virtual.

---

# 🧪 Ejecutar pruebas

Con el entorno activado:

```bash
python -m unittest discover -s tests -v
```

Actualmente se validan:

- segmentación;
- nombres de tiempo;
- defaults de proyecto;
- persistencia;
- filtros promocionales;
- encoder CPU;
- encoder NVENC.

---

# 📂 Directorios generados

## Videos cargados

```text
uploads/
```

## Resultados

```text
outputs/<proyecto>/
├── original/
└── vertical_9x16/
```

## Datos internos

```text
data/
├── projects.json
├── render_logs.jsonl
└── project_assets/
```

Estas carpetas contienen información local y no forman parte del código fuente versionado.

---

# 🧹 Limpieza

Desde el portal puedes:

- eliminar un proyecto;
- eliminar su video;
- eliminar sus outputs;
- eliminar hook/outro;
- limpiar todos los proyectos.

La opción **Limpiar todo** debe usarse con cuidado porque elimina archivos administrados por la herramienta.

---

# 🐛 Diagnóstico de errores FFmpeg

Cuando FFmpeg falla, el portal muestra:

```text
Ver detalle técnico de FFmpeg
```

Ese bloque permite revisar:

- encoder;
- filtros;
- streams;
- resolución;
- audio;
- mensajes del driver;
- errores NVENC.

También puedes revisar:

```text
data/render_logs.jsonl
```

---

# 🧯 Problemas frecuentes

## `ffmpeg` no se reconoce

Comprueba:

```bash
ffmpeg -version
```

Si Windows no reconoce el comando, agrega FFmpeg al `PATH`.

---

## `ffprobe` no se reconoce

```bash
ffprobe -version
```

FFprobe normalmente viene incluido con FFmpeg.

---

## No puedo activar el entorno en PowerShell

Ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Luego:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## NVENC aparece pero falla

Usa:

```text
Auto
```

El sistema intentará GPU y hará fallback a CPU.

También puedes forzar:

```text
CPU · libx264
```

---

## El navegador muestra una versión anterior

Usa:

```text
Ctrl + F5
```

para limpiar la caché del frontend.

---

## Quiero ver un clip recién regenerado

Los enlaces de clips incorporan un identificador para evitar que el navegador reutilice el MP4 anterior desde caché.

---

# ✅ Checklist final de la V1

Antes de fusionar `develop` con `main`:

- [ ] carga de video;
- [ ] FFprobe;
- [ ] generación de segmentos;
- [ ] preview;
- [ ] selección individual;
- [ ] Reel 9:16;
- [ ] formato original;
- [ ] branding activado;
- [ ] branding desactivado;
- [ ] solo clip;
- [ ] hook + clip;
- [ ] clip + outro;
- [ ] hook + clip + outro;
- [ ] fade;
- [ ] CPU;
- [ ] Auto;
- [ ] NVIDIA NVENC;
- [ ] cancelación;
- [ ] tiempo estimado;
- [ ] abrir carpeta;
- [ ] proyecto reciente;
- [ ] presets;
- [ ] logs;
- [ ] tests;
- [ ] modo claro;
- [ ] modo oscuro.

---

# 🗺️ Roadmap futuro — V2

Fuera de alcance de esta V1:

- Whisper;
- transcripción automática;
- subtítulos;
- corrección manual de subtítulos;
- estilos de subtítulos;
- procesamiento de múltiples videos en lote;
- colas persistentes;
- más templates visuales;
- perfiles avanzados de exportación.

La V1 queda deliberadamente cerrada antes de estas funciones para mantener una base estable.

---

# 📌 Estado del proyecto

```text
V1
Estado: validación final
Rama: develop
```

Después de completar el checklist:

```text
develop
   ↓
main
   ↓
V1 estable
```

---

# 👨‍💻 Autor

**AnderCode**

Web:

```text
anderson-bastidas.com
```

Proyecto desarrollado como herramienta local para automatizar la creación de contenido corto a partir de cursos y videos largos.
