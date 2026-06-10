import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from notion_client import Client
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from groq import Groq  # NUEVO: Cambiado de Gemini a Groq
import os
import sys

# ==================== CONFIGURACIÓN DE CREDENCIALES ====================

CONFIG_FILE = "config.json"

def load_config():
    """Carga la configuración desde el archivo JSON"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Guarda la configuración en el archivo JSON"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def show_config_window(is_first_time=False):
    """Muestra la ventana de configuración para ingresar API keys"""
    config = load_config()
    
    config_window = tk.Toplevel() if not is_first_time else tk.Tk()
    config_window.title("Configuración de API Keys")
    config_window.geometry("500x400")
    config_window.configure(bg="#f5f5f7")
    config_window.resizable(False, False)
    
    # Si es primera vez, hacer que no se pueda cerrar la ventana
    if is_first_time:
        config_window.protocol("WM_DELETE_WINDOW", lambda: None)
    else:
        # Hacer que la ventana sea modal
        config_window.transient()
        config_window.grab_set()
    
    font_style = ("Helvetica", 11)
    
    # Título
    title_label = tk.Label(
        config_window,
        text="🔑 Configuración de Credenciales",
        font=("Helvetica", 16, "bold"),
        bg="#f5f5f7",
        fg="#1d1d1f"
    )
    title_label.pack(pady=20)
    
    # Frame para los campos
    fields_frame = tk.Frame(config_window, bg="#f5f5f7")
    fields_frame.pack(pady=10, padx=30, fill="both", expand=True)
    
    # NOTION API KEY
    notion_label = tk.Label(
        fields_frame,
        text="Notion API Key:",
        font=font_style,
        bg="#f5f5f7",
        fg="#1d1d1f",
        anchor="w"
    )
    notion_label.pack(fill="x", pady=(5, 2))
    
    notion_entry = tk.Entry(
        fields_frame,
        font=font_style,
        bg="white",
        fg="#1d1d1f",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground="#d2d2d7",
        highlightcolor="#007aff",
        show="*"
    )
    notion_entry.insert(0, config.get("NOTION_API_KEY", ""))
    notion_entry.pack(fill="x", pady=(0, 10))
    
    # Crear menú contextual temporal para este widget
    def create_temp_context_menu(widget):
        context_menu = tk.Menu(widget, tearoff=0)
        context_menu.add_command(label="Cortar", command=lambda: widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="Copiar", command=lambda: widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Pegar", command=lambda: widget.event_generate("<<Paste>>"))
        context_menu.add_separator()
        context_menu.add_command(label="Seleccionar todo", command=lambda: widget.select_range(0, tk.END))
        widget.bind("<Button-3>", lambda e: context_menu.tk_popup(e.x_root, e.y_root))
        return context_menu
    
    create_temp_context_menu(notion_entry)
    
    # NOTION DATABASE ID
    db_label = tk.Label(
        fields_frame,
        text="Notion Database ID:",
        font=font_style,
        bg="#f5f5f7",
        fg="#1d1d1f",
        anchor="w"
    )
    db_label.pack(fill="x", pady=(5, 2))
    
    db_entry = tk.Entry(
        fields_frame,
        font=font_style,
        bg="white",
        fg="#1d1d1f",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground="#d2d2d7",
        highlightcolor="#007aff",
        show="*"
    )
    db_entry.insert(0, config.get("NOTION_DATABASE_ID", ""))
    db_entry.pack(fill="x", pady=(0, 10))
    create_temp_context_menu(db_entry)
    
    # GROQ API KEY (CAMBIADO DE GEMINI)
    groq_label = tk.Label(
        fields_frame,
        text="Groq API Key:",
        font=font_style,
        bg="#f5f5f7",
        fg="#1d1d1f",
        anchor="w"
    )
    groq_label.pack(fill="x", pady=(5, 2))
    
    groq_entry = tk.Entry(
        fields_frame,
        font=font_style,
        bg="white",
        fg="#1d1d1f",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground="#d2d2d7",
        highlightcolor="#007aff",
        show="*"
    )
    groq_entry.insert(0, config.get("GROQ_API_KEY", ""))
    groq_entry.pack(fill="x", pady=(0, 10))
    create_temp_context_menu(groq_entry)
    
    # Botón para mostrar/ocultar contraseñas
    show_password_var = tk.BooleanVar()
    
    def toggle_password():
        if show_password_var.get():
            notion_entry.config(show="")
            db_entry.config(show="")
            groq_entry.config(show="")
        else:
            notion_entry.config(show="*")
            db_entry.config(show="*")
            groq_entry.config(show="*")
    
    show_check = tk.Checkbutton(
        fields_frame,
        text="Mostrar claves",
        variable=show_password_var,
        command=toggle_password,
        bg="#f5f5f7",
        font=("Helvetica", 10),
        activebackground="#f5f5f7"
    )
    show_check.pack(pady=5)
    
    # Frame para botones
    button_frame = tk.Frame(config_window, bg="#f5f5f7")
    button_frame.pack(pady=20)
    
    def save_and_close():
        notion_key = notion_entry.get().strip()
        db_id = db_entry.get().strip()
        groq_key = groq_entry.get().strip()
        
        if not notion_key or not db_id or not groq_key:
            messagebox.showwarning(
                "Campos incompletos",
                "Por favor, completa todos los campos."
            )
            return
        
        new_config = {
            "NOTION_API_KEY": notion_key,
            "NOTION_DATABASE_ID": db_id,
            "GROQ_API_KEY": groq_key
        }
        
        save_config(new_config)
        
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
            result = messagebox.askyesno(
                "Salir",
                "¿Estás seguro de que deseas salir sin guardar?\nLa aplicación se cerrará."
            )
            if result:
                config_window.destroy()
                exit()
        else:
            config_window.destroy()
    
    # Botón Guardar
    save_button = tk.Button(
        button_frame,
        text="Guardar",
        command=save_and_close,
        bg="#007aff",
        fg="white",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        padx=30,
        pady=10,
        font=font_style,
        activebackground="#0063cc",
        activeforeground="white"
    )
    save_button.pack(side="left", padx=5)
    
    # Botón Cancelar
    cancel_button = tk.Button(
        button_frame,
        text="Cancelar" if not is_first_time else "Salir",
        command=cancel_action,
        bg="#8e8e93",
        fg="white",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        padx=30,
        pady=10,
        font=font_style,
        activebackground="#6e6e73",
        activeforeground="white"
    )
    cancel_button.pack(side="left", padx=5)
    
    # Centrar la ventana
    config_window.update_idletasks()
    width = config_window.winfo_width()
    height = config_window.winfo_height()
    x = (config_window.winfo_screenwidth() // 2) - (width // 2)
    y = (config_window.winfo_screenheight() // 2) - (height // 2)
    config_window.geometry(f'{width}x{height}+{x}+{y}')
    
    if is_first_time:
        config_window.mainloop()

def validate_config():
    """Valida que existan las credenciales"""
    config = load_config()
    
    if (not config.get("NOTION_API_KEY") or 
        not config.get("NOTION_DATABASE_ID") or 
        not config.get("GROQ_API_KEY")):
        return None
    
    return config

# ==================== FUNCIONES DE SCRAPING ====================

def scrape_job_post(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        title = extract_title(soup)
        company = extract_company(soup)
        description = extract_description(soup)
        fuente = extract_fuente(soup)
        
        return {
            "Empresa": company,
            "Puesto": title,
            "Descripción": description,
            "Fuente": fuente
        }
    
    except Exception as e:
        print(f"Error al procesar la URL: {e}")
        return None

def extract_title(soup):
    title = soup.find(["h1", "h2", "h3"])
    if title:
        return title.get_text(strip=True)
    return "Título no encontrado"

def extract_company(soup):
    company = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link")
    if company:
        return company.get_text(strip=True)
    return "Compañía no encontrada"

def extract_description(soup):
    description = soup.find("div", class_="show-more-less-html__markup")
    if description:
        return description.get_text(strip=True)
    return "Descripción no encontrada"

def extract_fuente(soup):
    fuente = soup.find("span", class_="sr-only")
    if fuente:
        return fuente.get_text(strip=True)
    return "fuente no encontrada"

# ==================== FUNCIÓN: EXTRAER CON GROQ ====================

def extract_with_groq(text):
    """Extrae información de una oferta laboral usando Groq AI"""
    try:
        prompt = f"""
Analiza el siguiente texto de una oferta laboral y extrae TODA la información de contacto en formato JSON.
Si algún campo no está presente, usa "No especificado".

TEXTO DE LA OFERTA:
{text}

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{{
    "Empresa": "nombre de la empresa",
    "Puesto": "título del puesto",
    "Descripción": "descripción completa del trabajo (máximo 2000 caracteres)",
    "Correo": "correo electrónico de contacto",
    "Teléfono": "número de teléfono de contacto"
}}

REGLAS CRÍTICAS PARA EXTRACCIÓN:
- Busca MUY CUIDADOSAMENTE el teléfono en TODO el texto
- Teléfonos pueden estar en formatos: +593 99 123 4567, +593991234567, 0991234567, (04) 123-4567, 04-1234567, etc.
- Busca palabras como "Teléfono:", "Tel:", "Celular:", "Móvil:", "Contacto:", "Llamar al:", "WhatsApp:" seguidas de números
- Si hay números que parecen teléfonos (10+ dígitos con espacios, guiones o paréntesis), son teléfonos
- Correos tienen formato: algo@algo.com
- Si encuentras un correo electrónico y no el nombre de la empresa, extrae el nombre de la empresa del dominio (ejemplo: contact@ifcode.com → "If Code")
- Si NO encuentras teléfono después de buscar EXHAUSTIVAMENTE, solo entonces usa "No especificado"
- Responde SOLO el JSON, sin texto adicional, sin markdown, sin bloques de código
"""
        
        # NUEVO: Llamada a Groq en lugar de Gemini
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modelo de Groq más potente
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en análisis de ofertas laborales. SIEMPRE buscas EXHAUSTIVAMENTE toda la información de contacto incluyendo correos y teléfonos. Respondes en formato JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Más bajo para ser más preciso
            max_tokens=2048
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Limpiar posibles markdown o caracteres extra
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()
        
        # Intentar parsear el JSON
        job_data = json.loads(result_text)
        
        # DEBUG: Mostrar lo que Groq extrajo
        print("=" * 50)
        print("DEBUG - Datos extraídos por Groq:")
        print(f"Empresa: {job_data.get('Empresa')}")
        print(f"Puesto: {job_data.get('Puesto')}")
        print(f"Correo: {job_data.get('Correo')}")
        print(f"Teléfono: {job_data.get('Teléfono')}")
        print("=" * 50)
        
        # Limitar descripción a 2000 caracteres
        if len(job_data.get("Descripción", "")) > 2000:
            job_data["Descripción"] = job_data["Descripción"][:2000]
        
        return job_data
    
    except Exception as e:
        print(f"Error al procesar con Groq: {e}")
        messagebox.showerror(
            "Error de Groq",
            f"No se pudo procesar el texto con IA:\n\n{e}\n\nVerifica tu API Key de Groq en Configuración."
        )
        return None

# ==================== FUNCIÓN PARA ENVIAR A NOTION ====================

def add_to_notion(job_data, job_url=None):
    """Envía los datos a Notion"""
    if job_data:
        description = job_data["Descripción"]
        if len(description) > 2000:
            description = description[:2000]
        
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        properties = {
            "Empresa": {"title": [{"text": {"content": job_data["Empresa"]}}]},
            "Puesto": {"rich_text": [{"text": {"content": job_data["Puesto"]}}]},
            "Descripción": {"rich_text": [{"text": {"content": description}}]},
            "Fuente": {"rich_text": [{"text": {"content": job_data.get("Fuente", "Texto manual")}}]},
            "Fecha de Postulación": {"date": {"start": current_date}}
        }
        
        # Combinar Correo y Teléfono en una sola columna "Contacto"
        contacto_info = []
        
        if job_data.get("Correo") and job_data["Correo"] != "No especificado":
            contacto_info.append(f"📧 {job_data['Correo']}")
        
        if job_data.get("Teléfono") and job_data["Teléfono"] != "No especificado":
            contacto_info.append(f"📱 {job_data['Teléfono']}")
        
        # Si hay información de contacto, agregarla a Notion
        if contacto_info:
            contacto_text = "\n".join(contacto_info)
            properties["Contacto"] = {"rich_text": [{"text": {"content": contacto_text}}]}
        
        # Solo agregar Enlace si existe
        if job_url:
            properties["Enlace"] = {"url": job_url}
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=properties
        )
        return True
    return False

# ==================== FUNCIONES DE LA GUI ====================

def on_submit_url():
    """Procesar oferta desde URL"""
    url = url_entry.get()
    
    if not url:
        result_label_url.config(text="Por favor ingrese una URL.", fg="red")
        return

    job_data = scrape_job_post(url)
    
    if job_data:
        success = add_to_notion(job_data, url)
        if success:
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
        success = add_to_notion(job_data)
        if success:
            result_label_text.config(
                text=f"✓ Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", 
                fg="green"
            )
            text_entry.delete("1.0", tk.END)
        else:
            result_label_text.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label_text.config(text="No se pudo procesar el texto. Verifica el formato.", fg="red")

def on_exit():
    root.quit()

def create_context_menu(widget):
    """Crea un menú contextual para un widget de entrada"""
    context_menu = tk.Menu(widget, tearoff=0)
    
    def copy_text():
        try:
            widget.clipboard_clear()
            if isinstance(widget, scrolledtext.ScrolledText):
                text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                text = widget.selection_get()
            widget.clipboard_append(text)
        except:
            pass
    
    def cut_text():
        try:
            copy_text()
            if isinstance(widget, scrolledtext.ScrolledText):
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def paste_text():
        try:
            text = widget.clipboard_get()
            if isinstance(widget, scrolledtext.ScrolledText):
                try:
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except:
                    pass
                widget.insert(tk.INSERT, text)
            else:
                try:
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except:
                    pass
                widget.insert(tk.INSERT, text)
        except:
            pass
    
    def select_all():
        if isinstance(widget, scrolledtext.ScrolledText):
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

def start_main_app():
    """Inicia la aplicación principal después de validar la configuración"""
    global root, url_entry, result_label_url, text_entry, result_label_text
    global notion, DATABASE_ID, groq_client
    
    config = load_config()
    
    NOTION_API_KEY = config["NOTION_API_KEY"]
    NOTION_DATABASE_ID = config["NOTION_DATABASE_ID"]
    GROQ_API_KEY = config["GROQ_API_KEY"]
    
    # Conectar con Notion
    try:
        notion = Client(auth=NOTION_API_KEY)
        DATABASE_ID = NOTION_DATABASE_ID
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar con Notion:\n\n{e}\n\nVerifica tu API Key en Configuración.")
        exit()
    
    # Configurar Groq (NUEVO)
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        messagebox.showerror(
            "Error de configuración Groq", 
            f"No se pudo configurar Groq:\n\n{e}\n\nVerifica tu API Key en Configuración."
        )
        exit()
    
    # ==================== CONFIGURAR LA GUI ====================
    
    root = tk.Tk()
    root.title("Registrar Oferta de Empleo en Notion")
    root.geometry("600x550")
    root.configure(bg="#f5f5f7")
    
    # Intentar agregar ícono
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    root.iconbitmap(resource_path("favicon.ico"))
    
    font_style = ("Helvetica", 12)
    
    # Menú
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="⚙️ Configuración", menu=settings_menu)
    settings_menu.add_command(label="Editar API Keys", command=lambda: show_config_window(False))
    
    # Crear sistema de pestañas
    tab_control = ttk.Notebook(root)
    
    # ========== TAB 1: DESDE URL ==========
    tab_url = tk.Frame(tab_control, bg="#f5f5f7")
    tab_control.add(tab_url, text="Desde URL")
    
    url_label = tk.Label(
        tab_url,
        text="Introduce la URL de la oferta de empleo:",
        font=font_style,
        bg="#f5f5f7",
        fg="#1d1d1f"
    )
    url_label.pack(pady=20)
    
    url_entry = tk.Entry(
        tab_url,
        width=50,
        font=font_style,
        bg="white",
        fg="#1d1d1f",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground="#d2d2d7",
        highlightcolor="#007aff"
    )
    url_entry.pack(pady=5)
    create_context_menu(url_entry)
    
    submit_button_url = tk.Button(
        tab_url,
        text="Agregar a Notion",
        command=on_submit_url,
        bg="#007aff",
        fg="white",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        padx=20,
        pady=10,
        font=font_style,
        activebackground="#0063cc",
        activeforeground="white"
    )
    submit_button_url.pack(pady=20)
    
    result_label_url = tk.Label(
        tab_url,
        text="",
        font=font_style,
        wraplength=500,
        bg="#f5f5f7",
        fg="#1d1d1f"
    )
    result_label_url.pack(pady=10)
    
    # ========== TAB 2: DESDE TEXTO ==========
    tab_text = tk.Frame(tab_control, bg="#f5f5f7")
    tab_control.add(tab_text, text="Desde Texto")
    
    text_label = tk.Label(
        tab_text,
        text="Pega el texto completo de la oferta de empleo:",
        font=font_style,
        bg="#f5f5f7",
        fg="#1d1d1f"
    )
    text_label.pack(pady=20)
    
    text_entry = scrolledtext.ScrolledText(
        tab_text,
        width=60,
        height=12,
        font=("Helvetica", 10),
        bg="white",
        fg="#1d1d1f",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground="#d2d2d7",
        highlightcolor="#007aff",
        wrap=tk.WORD
    )
    text_entry.pack(pady=5)
    create_context_menu(text_entry)
    
    submit_button_text = tk.Button(
        tab_text,
        text="Procesar con IA y Agregar",
        command=on_submit_text,
        bg="#007aff",
        fg="white",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        padx=20,
        pady=10,
        font=font_style,
        activebackground="#0063cc",
        activeforeground="white"
    )
    submit_button_text.pack(pady=10)
    
    result_label_text = tk.Label(
        tab_text,
        text="",
        font=font_style,
        wraplength=500,
        bg="#f5f5f7",
        fg="#1d1d1f"
    )
    result_label_text.pack(pady=10)
    
    # ========== EMPAQUETAR PESTAÑAS ==========
    tab_control.pack(expand=1, fill="both", padx=10, pady=10)
    
    # ========== BOTÓN DE SALIR ==========
    exit_button = tk.Button(
        root,
        text="Salir",
        command=on_exit,
        bg="#ff3b30",
        fg="white",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        padx=20,
        pady=10,
        font=font_style,
        activebackground="#cc2b24",
        activeforeground="white"
    )
    exit_button.pack(pady=10)
    
    # Iniciar la interfaz gráfica
    root.mainloop()

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    config = validate_config()
    
    if config is None:
        # Primera vez: mostrar ventana de configuración
        show_config_window(is_first_time=True)
    else:
        # Ya hay configuración: iniciar app principal
        start_main_app()