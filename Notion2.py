import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from notion_client import Client
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import google.generativeai as genai

# Configurar variables de entorno
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validar que las variables de entorno estén configuradas
if not NOTION_API_KEY or not NOTION_DATABASE_ID:
    raise ValueError("ERROR: Configura las variables NOTION_API_KEY y NOTION_DATABASE_ID")

if not GEMINI_API_KEY:
    raise ValueError("ERROR: Configura la variable GEMINI_API_KEY")

# Conectar con Notion
notion = Client(auth=NOTION_API_KEY)
DATABASE_ID = NOTION_DATABASE_ID

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ==================== FUNCIONES DE SCRAPING (SIN CAMBIOS) ====================

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

# ==================== NUEVA FUNCIÓN: EXTRAER CON GEMINI ====================

def extract_with_gemini(text):
    """Extrae información de una oferta laboral usando Gemini AI"""
    try:
        prompt = f"""
Analiza el siguiente texto de una oferta laboral y extrae la información en formato JSON.
Si algún campo no está presente, usa "No especificado".

TEXTO DE LA OFERTA:
{text}

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{{
    "Empresa": "nombre de la empresa",
    "Puesto": "título del puesto",
    "Descripción": "descripción completa del trabajo (máximo 2000 caracteres)"
}}

IMPORTANTE: 
- Si encuentras un correo electrónico y no el nombre de la empresa, extrae el nombre de la empresa del dominio (ejemplo: contact@ifcode.com → "If Code")
- Responde SOLO el JSON, sin texto adicional
- No uses markdown ni bloques de código
- La descripción debe resumir: responsabilidades, requisitos y beneficios si están presentes
"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Limpiar posibles markdown o caracteres extra
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()
        
        # Intentar parsear el JSON
        import json
        job_data = json.loads(result_text)
        
        # Limitar descripción a 2000 caracteres
        if len(job_data.get("Descripción", "")) > 2000:
            job_data["Descripción"] = job_data["Descripción"][:2000]
        
        return job_data
    
    except Exception as e:
        print(f"Error al procesar con Gemini: {e}")
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
    """Procesar oferta desde URL (funcionalidad original)"""
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
    """Procesar oferta desde texto plano usando Gemini"""
    text = text_entry.get("1.0", tk.END).strip()
    
    if not text:
        result_label_text.config(text="Por favor ingrese el texto de la oferta.", fg="red")
        return
    
    result_label_text.config(text="Procesando con IA...", fg="blue")
    root.update()  # Actualizar la GUI
    
    job_data = extract_with_gemini(text)
    
    if job_data:
        # Agregar fuente como "Texto manual"
        job_data["Fuente"] = "Texto manual"
        success = add_to_notion(job_data)
        if success:
            result_label_text.config(
                text=f"✓ Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", 
                fg="green"
            )
            text_entry.delete("1.0", tk.END)  # Limpiar el área de texto
        else:
            result_label_text.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label_text.config(text="No se pudo procesar el texto. Verifica el formato.", fg="red")

def on_exit():
    root.quit()

# ==================== CONFIGURAR LA GUI ====================

root = tk.Tk()
root.title("Registrar Oferta de Empleo en Notion")
root.geometry("600x500")
root.configure(bg="#f5f5f7")

font_style = ("Helvetica", 12)

# Crear sistema de pestañas
tab_control = ttk.Notebook(root)

# ========== TAB 1: DESDE URL (FUNCIONALIDAD ORIGINAL) ==========
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

# ========== TAB 2: DESDE TEXTO (NUEVA FUNCIONALIDAD) ==========
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

# ========== BOTÓN DE SALIR (GLOBAL) ==========
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