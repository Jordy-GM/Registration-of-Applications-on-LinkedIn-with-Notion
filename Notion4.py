import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from notion_client import Client
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
import base64
import sys
from io import BytesIO
from groq import Groq
from PIL import Image, ImageGrab, ImageTk

# ==================== ESTILO / CONSTANTES DE UI ====================
# Centralizar los colores y fuentes evita repetirlos en cada widget.

BG = "#f5f5f7"
TEXT = "#1d1d1f"
BORDER = "#d2d2d7"
FOCUS = "#007aff"
WHITE = "white"

BLUE, BLUE_ACTIVE = "#007aff", "#0063cc"
PURPLE, PURPLE_ACTIVE = "#5856d6", "#413fa8"
GRAY, GRAY_ACTIVE = "#8e8e93", "#6e6e73"
RED, RED_ACTIVE = "#ff3b30", "#cc2b24"

FONT = ("Helvetica", 12)
FONT_SMALL = ("Helvetica", 10)
FONT_TITLE = ("Helvetica", 16, "bold")

CONFIG_FILE = "config.json"

# Modelos de Groq. Groq actualiza su catálogo con frecuencia; si alguno se
# retira, revisa el reemplazo vigente en https://console.groq.com/docs/models
GROQ_TEXT_MODEL = "llama-3.3-70b-versatile"
GROQ_VISION_MODEL = "qwen/qwen3.6-27b"

NOTION_VERSION = "2026-03-11"
MAX_DESCRIPTION_LEN = 2000

PREVIEW_BOX_WIDTH = 460
PREVIEW_BOX_HEIGHT = 300

# ==================== HELPERS DE WIDGETS (evitan repetir estilos) ====================

def make_label(parent, text, font=FONT, fg=TEXT, bg=BG, **kwargs):
    return tk.Label(parent, text=text, font=font, bg=bg, fg=fg, **kwargs)

def make_entry(parent, width=None, show=None, font=FONT):
    kwargs = {"font": font, "bg": WHITE, "fg": TEXT, "relief": tk.FLAT,
              "borderwidth": 0, "highlightthickness": 1,
              "highlightbackground": BORDER, "highlightcolor": FOCUS}
    if width:
        kwargs["width"] = width
    if show:
        kwargs["show"] = show
    return tk.Entry(parent, **kwargs)

def make_button(parent, text, command, bg=BLUE, active_bg=BLUE_ACTIVE,
                 font=FONT, padx=20, pady=10):
    return tk.Button(
        parent, text=text, command=command, bg=bg, fg="white",
        relief=tk.FLAT, borderwidth=0, highlightthickness=0,
        padx=padx, pady=pady, font=font,
        activebackground=active_bg, activeforeground="white"
    )

def make_result_label(parent):
    return tk.Label(parent, text="", font=FONT, wraplength=500, bg=BG, fg=TEXT)

# ==================== CONFIGURACIÓN DE CREDENCIALES ====================

def load_config():
    """Carga la configuración desde el archivo JSON"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config):
    """Guarda la configuración en el archivo JSON"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def validate_config():
    """Valida que existan las credenciales"""
    config = load_config()
    required = ("NOTION_API_KEY", "NOTION_DATABASE_ID", "GROQ_API_KEY")
    if not all(config.get(k) for k in required):
        return None
    return config

def show_config_window(is_first_time=False):
    """Muestra la ventana de configuración para ingresar API keys"""
    config = load_config()

    config_window = tk.Toplevel() if not is_first_time else tk.Tk()
    config_window.title("Configuración de API Keys")
    config_window.geometry("500x400")
    config_window.configure(bg=BG)
    config_window.resizable(False, False)

    if is_first_time:
        config_window.protocol("WM_DELETE_WINDOW", lambda: None)
    else:
        config_window.transient()
        config_window.grab_set()

    make_label(config_window, "🔑 Configuración de Credenciales", font=FONT_TITLE).pack(pady=20)

    fields_frame = tk.Frame(config_window, bg=BG)
    fields_frame.pack(pady=10, padx=30, fill="both", expand=True)

    def add_field(label_text, key):
        """Crea una etiqueta + campo de contraseña con menú contextual, y devuelve el Entry."""
        make_label(fields_frame, label_text, font=("Helvetica", 11), anchor="w").pack(fill="x", pady=(5, 2))
        entry = make_entry(fields_frame, font=("Helvetica", 11), show="*")
        entry.insert(0, config.get(key, ""))
        entry.pack(fill="x", pady=(0, 10))
        create_context_menu(entry)
        return entry

    notion_entry = add_field("Notion API Key:", "NOTION_API_KEY")
    db_entry = add_field("Notion Database ID:", "NOTION_DATABASE_ID")
    groq_entry = add_field("Groq API Key:", "GROQ_API_KEY")

    # Botón para mostrar/ocultar contraseñas
    show_password_var = tk.BooleanVar()

    def toggle_password():
        show = "" if show_password_var.get() else "*"
        for entry in (notion_entry, db_entry, groq_entry):
            entry.config(show=show)

    tk.Checkbutton(
        fields_frame, text="Mostrar claves", variable=show_password_var,
        command=toggle_password, bg=BG, font=FONT_SMALL, activebackground=BG
    ).pack(pady=5)

    button_frame = tk.Frame(config_window, bg=BG)
    button_frame.pack(pady=20)

    def save_and_close():
        notion_key = notion_entry.get().strip()
        db_id = db_entry.get().strip()
        groq_key = groq_entry.get().strip()

        if not notion_key or not db_id or not groq_key:
            messagebox.showwarning("Campos incompletos", "Por favor, completa todos los campos.")
            return

        save_config({
            "NOTION_API_KEY": notion_key,
            "NOTION_DATABASE_ID": db_id,
            "GROQ_API_KEY": groq_key
        })

        if is_first_time:
            messagebox.showinfo(
                "Configuración guardada",
                "Las credenciales se guardaron correctamente.\n\nLa aplicación se iniciará ahora."
            )
            config_window.destroy()
            start_main_app()
        else:
            messagebox.showinfo(
                "Configuración guardada",
                "Las credenciales se guardaron correctamente.\n\nPor favor, reinicia la aplicación."
            )
            config_window.destroy()

    def cancel_action():
        if is_first_time:
            if messagebox.askyesno("Salir", "¿Estás seguro de que deseas salir sin guardar?\nLa aplicación se cerrará."):
                config_window.destroy()
                exit()
        else:
            config_window.destroy()

    make_button(button_frame, "Guardar", save_and_close, font=("Helvetica", 11), padx=30).pack(side="left", padx=5)
    make_button(
        button_frame, "Salir" if is_first_time else "Cancelar", cancel_action,
        bg=GRAY, active_bg=GRAY_ACTIVE, font=("Helvetica", 11), padx=30
    ).pack(side="left", padx=5)

    # Centrar la ventana
    config_window.update_idletasks()
    width, height = config_window.winfo_width(), config_window.winfo_height()
    x = (config_window.winfo_screenwidth() // 2) - (width // 2)
    y = (config_window.winfo_screenheight() // 2) - (height // 2)
    config_window.geometry(f'{width}x{height}+{x}+{y}')

    if is_first_time:
        config_window.mainloop()

# ==================== FUNCIONES DE SCRAPING ====================

def extract_title(soup):
    title = soup.find(["h1", "h2", "h3"])
    return title.get_text(strip=True) if title else "Título no encontrado"

def extract_company(soup):
    company = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link")
    return company.get_text(strip=True) if company else "Compañía no encontrada"

def extract_description(soup):
    description = soup.find("div", class_="show-more-less-html__markup")
    return description.get_text(strip=True) if description else "Descripción no encontrada"

def extract_fuente(soup):
    fuente = soup.find("span", class_="sr-only")
    return fuente.get_text(strip=True) if fuente else "fuente no encontrada"

def scrape_job_post(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return {
            "Empresa": extract_company(soup),
            "Puesto": extract_title(soup),
            "Descripción": extract_description(soup),
            "Fuente": extract_fuente(soup)
        }
    except Exception as e:
        print(f"Error al procesar la URL: {e}")
        return None

# ==================== HELPERS COMPARTIDOS: GROQ / JSON ====================

JOB_EXTRACTION_RULES = """
REGLAS CRÍTICAS PARA EXTRACCIÓN:
- Busca MUY CUIDADOSAMENTE el teléfono en TODO el texto
- Teléfonos pueden estar en formatos: +593 99 123 4567, +593991234567, 0991234567, (04) 123-4567, 04-1234567, etc.
- Busca palabras como "Teléfono:", "Tel:", "Celular:", "Móvil:", "Contacto:", "Llamar al:", "WhatsApp:" seguidas de números
- Correos tienen formato: algo@algo.com
- Si encuentras un correo electrónico y no el nombre de la empresa, extrae el nombre de la empresa del dominio (ejemplo: contact@ifcode.com → "If Code")
- Si NO encuentras teléfono después de buscar EXHAUSTIVAMENTE, solo entonces usa "No especificado"
- Responde SOLO el JSON, sin texto adicional, sin markdown, sin bloques de código
"""

JOB_JSON_STRUCTURE = """{
    "Empresa": "nombre de la empresa",
    "Puesto": "título del puesto",
    "Descripción": "descripción completa del trabajo (máximo 2000 caracteres)",
    "Correo": "correo electrónico de contacto",
    "Teléfono": "número de teléfono de contacto"
}"""

def clean_json_response(text):
    """Quita los bloques de markdown (```json ... ```) que a veces envuelven la respuesta"""
    text = text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()
    return text

def debug_print_job_data(source_label, job_data):
    print("=" * 50)
    print(f"DEBUG - Datos extraídos por Groq ({source_label}):")
    print(f"Empresa: {job_data.get('Empresa')}")
    print(f"Puesto: {job_data.get('Puesto')}")
    print(f"Correo: {job_data.get('Correo')}")
    print(f"Teléfono: {job_data.get('Teléfono')}")
    print("=" * 50)

def finalize_job_data(job_data, source_label):
    """Trunca la descripción y muestra el debug; común a texto e imagen"""
    debug_print_job_data(source_label, job_data)
    if len(job_data.get("Descripción", "")) > MAX_DESCRIPTION_LEN:
        job_data["Descripción"] = job_data["Descripción"][:MAX_DESCRIPTION_LEN]
    return job_data

# ==================== FUNCIÓN: EXTRAER CON GROQ (TEXTO) ====================

def extract_with_groq(text):
    """Extrae información de una oferta laboral usando Groq AI (texto)"""
    try:
        prompt = f"""
Analiza el siguiente texto de una oferta laboral y extrae TODA la información de contacto en formato JSON.
Si algún campo no está presente, usa "No especificado".

TEXTO DE LA OFERTA:
{text}

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{JOB_JSON_STRUCTURE}
{JOB_EXTRACTION_RULES}

REGLAS ESPECÍFICAS PARA "Descripción":
- El campo "Descripción" debe ser una TRANSCRIPCIÓN COMPLETA Y LITERAL de TODO el texto de la
  publicación, de principio a fin, línea por línea, en el mismo orden en que aparece.
- NO resumas, NO omitas ni "filtres" nada por considerarlo poco relevante para el puesto.
- Incluye TODO sin excepción: título del puesto, cuerpo del anuncio, requisitos, emojis,
  enlaces de postulación (ej. "Postula AHORA: https://..."), textos de cierre como
  "Recibe alertas instantáneas de empleo: ...", y llamados a la acción como
  "Like + Comparte para ayudar a freelancers!".
- Si hay un enlace visible (aunque esté acortado, como lnkd.in/xxxxx), transcríbelo tal cual
  aparece en el texto.
- Preserva los saltos de línea/párrafos usando \\n para separar secciones, igual que en la imagen.
"""
        response = groq_client.chat.completions.create(
            model=GROQ_TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en análisis de ofertas laborales. SIEMPRE buscas EXHAUSTIVAMENTE toda la información de contacto incluyendo correos y teléfonos. Respondes en formato JSON válido."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2048
        )

        job_data = json.loads(clean_json_response(response.choices[0].message.content))
        return finalize_job_data(job_data, "texto")

    except Exception as e:
        print(f"Error al procesar con Groq: {e}")
        messagebox.showerror(
            "Error de Groq",
            f"No se pudo procesar el texto con IA:\n\n{e}\n\nVerifica tu API Key de Groq en Configuración."
        )
        return None

# ==================== FUNCIÓN: IMÁGENES (conversión + EXTRAER CON GROQ VISION) ====================

def pil_image_to_jpeg_bytes(pil_image):
    """Convierte una imagen PIL a bytes JPEG (convierte a RGB si tiene transparencia/paleta)"""
    buffer = BytesIO()
    img = pil_image.copy()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()

def encode_pil_image_to_base64(pil_image):
    """Convierte una imagen PIL a una cadena base64 en formato JPEG"""
    return base64.b64encode(pil_image_to_jpeg_bytes(pil_image)).decode("utf-8")


def extract_with_groq_image(base64_image):
    """Extrae información de una oferta laboral a partir de una imagen usando Groq Vision"""
    try:
        prompt = f"""
Analiza esta imagen de una publicación de oferta laboral (puede ser una captura de pantalla de
LinkedIn, un flyer, un aviso, etc.) y extrae la información en formato JSON.
Si algún campo no está presente, usa "No especificado".
 
Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{JOB_JSON_STRUCTURE}
{JOB_EXTRACTION_RULES}
- Lee CUIDADOSAMENTE todo el texto visible en la imagen, incluyendo letras pequeñas, pies de página y logos con texto.
 
REGLAS ESPECÍFICAS PARA "Descripción":
- El campo "Descripción" debe ser una TRANSCRIPCIÓN COMPLETA Y LITERAL de TODO el texto de la
  publicación, de principio a fin, línea por línea, en el mismo orden en que aparece.
- NO resumas, NO omitas ni "filtres" nada por considerarlo poco relevante para el puesto.
- Incluye TODO sin excepción: título del puesto, cuerpo del anuncio, requisitos, emojis,
  enlaces de postulación (ej. "Postula AHORA: https://..."), textos de cierre como
  "Recibe alertas instantáneas de empleo: ...", y llamados a la acción como
  "Like + Comparte para ayudar a freelancers!".
- Si hay un enlace visible (aunque esté acortado, como lnkd.in/xxxxx), transcríbelo tal cual
  aparece en el texto.
- Preserva los saltos de línea/párrafos usando \\n para separar secciones, igual que en la imagen.
"""
        response = groq_client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=2048,
            # qwen3.6-27b es un modelo de razonamiento: sin esto, la respuesta
            # puede quedar entera en el "pensamiento interno" y dejar
            # message.content vacío, causando errores de JSON.
            reasoning_effort="none",
            reasoning_format="hidden",
            response_format={"type": "json_object"}
        )

        result_text = clean_json_response(
            response.choices[0].message.content or "")
        print("DEBUG - Respuesta cruda de Groq (imagen):",
              repr(result_text)[:500])

        if not result_text:
            raise ValueError(
                "El modelo devolvió una respuesta vacía. Intenta de nuevo o usa una imagen más nítida."
            )

        job_data = json.loads(result_text)
        return finalize_job_data(job_data, "imagen")

    except Exception as e:
        print(f"Error al procesar la imagen con Groq: {e}")
        messagebox.showerror(
            "Error de Groq",
            f"No se pudo procesar la imagen con IA:\n\n{e}\n\nVerifica tu API Key de Groq en Configuración."
        )
        return None
# ==================== FUNCIÓN: SUBIR IMAGEN A NOTION ====================

def upload_image_to_notion(pil_image):
    """
    Sube una imagen a Notion usando el Direct Upload API (file_uploads) y
    devuelve (file_upload_id, filename) listos para adjuntar a una propiedad.
    """
    image_bytes = pil_image_to_jpeg_bytes(pil_image)
    filename = f"oferta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    auth_headers = {"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": NOTION_VERSION}

    create_response = requests.post(
        "https://api.notion.com/v1/file_uploads",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={"filename": filename, "content_type": "image/jpeg"}
    )
    create_response.raise_for_status()
    upload_id = create_response.json()["id"]

    send_response = requests.post(
        f"https://api.notion.com/v1/file_uploads/{upload_id}/send",
        headers=auth_headers,
        files={"file": (filename, image_bytes, "image/jpeg")}
    )
    send_response.raise_for_status()

    return upload_id, filename

# ==================== FUNCIÓN PARA ENVIAR A NOTION ====================

def add_to_notion(job_data, job_url=None, pil_image=None):
    """Envía los datos a Notion. Si se pasa pil_image, también sube y adjunta la imagen
    a la propiedad 'Imagenes' (tipo Files & media)."""
    if not job_data:
        return False

    description = job_data["Descripción"][:MAX_DESCRIPTION_LEN]
    current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    properties = {
        "Empresa": {"title": [{"text": {"content": job_data["Empresa"]}}]},
        "Puesto": {"rich_text": [{"text": {"content": job_data["Puesto"]}}]},
        "Descripción": {"rich_text": [{"text": {"content": description}}]},
        "Fuente": {"rich_text": [{"text": {"content": job_data.get("Fuente", "Texto manual")}}]},
        "Fecha de Postulación": {"date": {"start": current_date}}
    }

    # Combinar Correo y Teléfono en una sola columna "Contacto"
    contacto_info = [
        f"📧 {job_data[key]}" if key == "Correo" else f"📱 {job_data[key]}"
        for key in ("Correo", "Teléfono")
        if job_data.get(key) and job_data[key] != "No especificado"
    ]
    if contacto_info:
        properties["Contacto"] = {"rich_text": [{"text": {"content": "\n".join(contacto_info)}}]}

    if job_url:
        properties["Enlace"] = {"url": job_url}

    if pil_image is not None:
        try:
            upload_id, filename = upload_image_to_notion(pil_image)
            properties["Imagenes"] = {
                "files": [{"type": "file_upload", "file_upload": {"id": upload_id}, "name": filename}]
            }
        except Exception as e:
            print(f"No se pudo subir la imagen a Notion: {e}")
            # No bloqueamos el guardado del resto de datos si falla la subida de la imagen

    notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
    return True

# ==================== FUNCIONES DE LA GUI: PESTAÑAS ====================

def on_submit_url():
    """Procesar oferta desde URL"""
    url = url_entry.get()
    if not url:
        result_label_url.config(text="Por favor ingrese una URL.", fg="red")
        return

    result_label_url.config(text="Procesando URL...", fg="blue")
    root.update()

    job_data = scrape_job_post(url)
    if job_data:
        if add_to_notion(job_data, url):
            result_label_url.config(text=f"✓ Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", fg="green")
        else:
            result_label_url.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label_url.config(text="No se pudieron extraer los datos de la URL.", fg="red")

    url_entry.delete(0, tk.END)

def on_submit_text():
    """Procesar oferta desde texto plano usando Groq"""
    text = text_entry.get("1.0", tk.END).strip()
    if not text:
        result_label_text.config(text="Por favor ingrese el texto de la oferta.", fg="red")
        return

    result_label_text.config(text="Procesando con IA (Groq)...", fg="blue")
    root.update()

    job_data = extract_with_groq(text)
    if job_data:
        job_data["Fuente"] = "Texto manual"
        if add_to_notion(job_data):
            result_label_text.config(text=f"✓ Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", fg="green")
            text_entry.delete("1.0", tk.END)
        else:
            result_label_text.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label_text.config(text="No se pudo procesar el texto. Verifica el formato.", fg="red")

# ---------- pestaña "Desde Imagen" ----------

current_image = None           # objeto PIL.Image cargado (subido o pegado)
current_image_preview = None   # referencia al ImageTk.PhotoImage (evita garbage collection)

def display_image_preview(pil_image):
    """Muestra una vista previa de la imagen, redimensionada para caber completa en el cuadro"""
    global current_image_preview
    preview_img = pil_image.copy()
    preview_img.thumbnail((PREVIEW_BOX_WIDTH - 20, PREVIEW_BOX_HEIGHT - 20))
    current_image_preview = ImageTk.PhotoImage(preview_img)
    image_preview_label.config(image=current_image_preview, text="")
    image_preview_label.image = current_image_preview

def select_image_file():
    """Abre un diálogo para seleccionar una imagen desde archivos"""
    global current_image
    file_path = filedialog.askopenfilename(
        title="Selecciona una imagen de la oferta laboral",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp"), ("Todos los archivos", "*.*")]
    )
    if not file_path:
        return
    try:
        current_image = Image.open(file_path)
        display_image_preview(current_image)
        result_label_image.config(text="Imagen cargada. Presiona 'Procesar con IA y Agregar'.", fg=TEXT)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n\n{e}")

def paste_image_clipboard(event=None):
    """Pega una imagen copiada al portapapeles (Ctrl+V, botón, o menú contextual)"""
    global current_image
    try:
        clipboard_content = ImageGrab.grabclipboard()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo acceder al portapapeles:\n\n{e}")
        return

    if not clipboard_content:
        result_label_image.config(text="No hay ninguna imagen en el portapapeles.", fg="red")
        return

    if isinstance(clipboard_content, list):
        try:
            current_image = Image.open(clipboard_content[0])
        except Exception as e:
            messagebox.showerror("Error", f"El portapapeles no contiene una imagen válida:\n\n{e}")
            return
    else:
        current_image = clipboard_content

    display_image_preview(current_image)
    result_label_image.config(text="Imagen pegada. Presiona 'Procesar con IA y Agregar'.", fg=TEXT)

def clear_image(clear_message=True):
    """Limpia la imagen cargada actualmente"""
    global current_image, current_image_preview
    current_image = None
    current_image_preview = None
    image_preview_label.config(image="", text="Sin imagen cargada\n(clic derecho para pegar)")
    image_preview_label.image = None
    if clear_message:
        result_label_image.config(text="")

def on_submit_image():
    """Procesar oferta desde imagen usando Groq Vision"""
    if current_image is None:
        result_label_image.config(text="Primero sube o pega una imagen.", fg="red")
        return

    result_label_image.config(text="Procesando imagen con IA (Groq)...", fg="blue")
    root.update()

    try:
        base64_image = encode_pil_image_to_base64(current_image)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo preparar la imagen:\n\n{e}")
        result_label_image.config(text="Error al preparar la imagen.", fg="red")
        return

    job_data = extract_with_groq_image(base64_image)
    if job_data:
        job_data["Fuente"] = "Imagen"
        if add_to_notion(job_data, pil_image=current_image):
            clear_image(clear_message=False)
            result_label_image.config(text=f"✓ Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", fg="green")
        else:
            result_label_image.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label_image.config(text="No se pudo procesar la imagen. Verifica que el texto sea legible.", fg="red")

def on_exit():
    root.quit()

# ==================== MENÚ CONTEXTUAL COMPARTIDO ====================

def create_context_menu(widget):
    """Crea un menú contextual (Cortar/Copiar/Pegar/Seleccionar todo) para Entry o ScrolledText"""
    context_menu = tk.Menu(widget, tearoff=0)
    is_scrolled = isinstance(widget, scrolledtext.ScrolledText)

    def copy_text():
        try:
            widget.clipboard_clear()
            text = widget.get(tk.SEL_FIRST, tk.SEL_LAST) if is_scrolled else widget.selection_get()
            widget.clipboard_append(text)
        except Exception:
            pass

    def cut_text():
        try:
            copy_text()
            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except Exception:
            pass

    def paste_text():
        try:
            text = widget.clipboard_get()
            try:
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except Exception:
                pass
            widget.insert(tk.INSERT, text)
        except Exception:
            pass

    def select_all():
        if is_scrolled:
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        else:
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)

    context_menu.add_command(label="Cortar", command=cut_text, accelerator="Ctrl+X")
    context_menu.add_command(label="Copiar", command=copy_text, accelerator="Ctrl+C")
    context_menu.add_command(label="Pegar", command=paste_text, accelerator="Ctrl+V")
    context_menu.add_separator()
    context_menu.add_command(label="Seleccionar todo", command=select_all, accelerator="Ctrl+A")

    def show_context_menu(event):
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    widget.bind("<Button-3>", show_context_menu)
    widget.bind("<Button-2>", show_context_menu)
    return context_menu

# ==================== CONSTRUCCIÓN DE PESTAÑAS ====================

def build_url_tab(tab_control):
    global url_entry, result_label_url

    tab = tk.Frame(tab_control, bg=BG)
    tab_control.add(tab, text="Desde URL")

    make_label(tab, "Introduce la URL de la oferta de empleo:").pack(pady=20)

    url_entry = make_entry(tab, width=50)
    url_entry.pack(pady=5)
    create_context_menu(url_entry)

    make_button(tab, "Agregar a Notion", on_submit_url).pack(pady=20)

    result_label_url = make_result_label(tab)
    result_label_url.pack(pady=10)

def build_text_tab(tab_control):
    global text_entry, result_label_text

    tab = tk.Frame(tab_control, bg=BG)
    tab_control.add(tab, text="Desde Texto")

    make_label(tab, "Pega el texto completo de la oferta de empleo:").pack(pady=20)

    text_entry = scrolledtext.ScrolledText(
        tab, width=60, height=12, font=FONT_SMALL, bg=WHITE, fg=TEXT,
        relief=tk.FLAT, borderwidth=0, highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=FOCUS, wrap=tk.WORD
    )
    text_entry.pack(pady=5)
    create_context_menu(text_entry)

    make_button(tab, "Procesar con IA y Agregar", on_submit_text).pack(pady=10)

    result_label_text = make_result_label(tab)
    result_label_text.pack(pady=10)

def build_image_tab(tab_control):
    global image_preview_label, result_label_image

    tab = tk.Frame(tab_control, bg=BG)
    tab_control.add(tab, text="Desde Imagen")

    make_label(tab, "Sube una imagen o pega una captura (Ctrl+V) de la oferta laboral:").pack(pady=(20, 10))

    buttons_frame = tk.Frame(tab, bg=BG)
    buttons_frame.pack(pady=5)
    make_button(buttons_frame, "📁 Subir Imagen", select_image_file,
                font=("Helvetica", 11), padx=15, pady=8).pack(side="left", padx=5)
    make_button(buttons_frame, "📋 Pegar (Ctrl+V)", paste_image_clipboard,
                bg=PURPLE, active_bg=PURPLE_ACTIVE, font=("Helvetica", 11), padx=15, pady=8).pack(side="left", padx=5)
    make_button(buttons_frame, "🗑️ Limpiar", clear_image,
                bg=GRAY, active_bg=GRAY_ACTIVE, font=("Helvetica", 11), padx=15, pady=8).pack(side="left", padx=5)

    # Contenedor de tamaño fijo real en píxeles para que la imagen se vea completa
    preview_container = tk.Frame(tab, width=PREVIEW_BOX_WIDTH, height=PREVIEW_BOX_HEIGHT,
                                  bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
    preview_container.pack(pady=15)
    preview_container.pack_propagate(False)

    image_preview_label = make_label(
        preview_container, "Sin imagen cargada\n(clic derecho para pegar)",
        font=FONT_SMALL, fg=GRAY, bg=WHITE, justify="center"
    )
    image_preview_label.pack(fill="both", expand=True)

    # Menú contextual (clic derecho) para pegar/subir/limpiar directamente en el cuadro
    image_context_menu = tk.Menu(image_preview_label, tearoff=0)
    image_context_menu.add_command(label="📋 Pegar imagen", command=paste_image_clipboard)
    image_context_menu.add_command(label="📁 Subir imagen...", command=select_image_file)
    image_context_menu.add_separator()
    image_context_menu.add_command(label="🗑️ Limpiar", command=lambda: clear_image())

    def show_image_context_menu(event):
        try:
            image_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            image_context_menu.grab_release()

    image_preview_label.bind("<Button-3>", show_image_context_menu)
    preview_container.bind("<Button-3>", show_image_context_menu)

    make_button(tab, "Procesar con IA y Agregar", on_submit_image).pack(pady=5)

    result_label_image = make_result_label(tab)
    result_label_image.pack(pady=10)

    # Permitir pegar con Ctrl+V mientras esta pestaña está activa
    tab.bind("<Control-v>", paste_image_clipboard)
    image_preview_label.bind("<Control-v>", paste_image_clipboard)
    image_preview_label.bind("<Button-1>", lambda e: image_preview_label.focus_set())
    image_preview_label.focus_set()

# ==================== APLICACIÓN PRINCIPAL ====================

def start_main_app():
    """Inicia la aplicación principal después de validar la configuración"""
    global root, notion, DATABASE_ID, groq_client, NOTION_API_KEY

    config = load_config()
    NOTION_API_KEY = config["NOTION_API_KEY"]
    DATABASE_ID = config["NOTION_DATABASE_ID"]
    GROQ_API_KEY = config["GROQ_API_KEY"]

    try:
        notion = Client(auth=NOTION_API_KEY)
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar con Notion:\n\n{e}\n\nVerifica tu API Key en Configuración.")
        exit()

    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        messagebox.showerror("Error de configuración Groq", f"No se pudo configurar Groq:\n\n{e}\n\nVerifica tu API Key en Configuración.")
        exit()

    # ---------- GUI ----------
    root = tk.Tk()
    root.title("Registrar Oferta de Empleo en Notion")
    root.geometry("620x650")
    root.configure(bg=BG)

    def resource_path(relative_path):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    try:
        root.iconbitmap(resource_path("favicon.ico"))
    except Exception as e:
        print(f"No se pudo cargar el icono: {e}")

    menubar = tk.Menu(root)
    root.config(menu=menubar)
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="⚙️ Configuración", menu=settings_menu)
    settings_menu.add_command(label="Editar API Keys", command=lambda: show_config_window(False))

    tab_control = ttk.Notebook(root)
    build_url_tab(tab_control)
    build_text_tab(tab_control)
    build_image_tab(tab_control)
    tab_control.pack(expand=1, fill="both", padx=10, pady=10)

    make_button(root, "Salir", on_exit, bg=RED, active_bg=RED_ACTIVE).pack(pady=10)

    root.mainloop()

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    config = validate_config()
    if config is None:
        show_config_window(is_first_time=True)
    else:
        start_main_app()