import tkinter as tk
from tkinter import messagebox
from notion_client import Client
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Conectar con Notion
notion = Client(auth="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")

# ID de la base de datos de Notion
DATABASE_ID = "1927803780f880689fb6c59ee4469e13"

# Función para extraer datos de la URL
def scrape_job_post(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Intentar extraer el título (usando diferentes etiquetas y clases comunes)
        title = extract_title(soup)
        
        # Intentar extraer la compañía (usando diferentes etiquetas y clases comunes)
        company = extract_company(soup)
        
        # Intentar extraer la descripción (usando diferentes selectores comunes)
        description = extract_description(soup)
        
        Fuente = extract_fuente(soup)  # Añadir la URL de la oferta de empleo
        
        return {
            "Empresa": company,
            "Puesto": title,
            "Descripción": description,  # Añadir descripción
            "Fuente": Fuente  # Añadir la URL de la oferta
        }
    
    except Exception as e:
        print(f"Error al procesar la URL: {e}")
        return None

# Función para extraer el título del puesto
def extract_title(soup):
    title = soup.find(["h1", "h2", "h3"])  # Verifica h1, h2, h3 como posibles etiquetas
    if title:
        return title.get_text(strip=True)
    return "Título no encontrado"

# Función para extraer el nombre de la empresa
def extract_company(soup):
    company = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link")
    if company:
        return company.get_text(strip=True)
    return "Compañía no encontrada"

# Función para extraer la descripción del trabajo
def extract_description(soup):
    description = soup.find("div", class_="show-more-less-html__markup")  # Ajusta esta clase al selector correcto
    if description:
        return description.get_text(strip=True)
    return "Descripción no encontrada"

# Función para extraer la descripción del trabajo
def extract_fuente(soup):
    description = soup.find("span", class_="sr-only")  # Ajusta esta clase al selector correcto
    if description:
        return description.get_text(strip=True)
    return "fuente no encontrada"

# Función para enviar los datos a Notion
def add_to_notion(job_data, job_url):
    if job_data:
        # Limitar la longitud de la descripción a 2000 caracteres
        description = job_data["Descripción"]
        if len(description) > 2000:
            description = description[:2000]  # Cortar el texto si es mayor a 2000 caracteres
        
        # Obtener la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # Formato ISO 8601 para Notion
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Empresa": {"title": [{"text": {"content": job_data["Empresa"]}}]},
                "Puesto": {"rich_text": [{"text": {"content": job_data["Puesto"]}}]},
                "Descripción": {"rich_text": [{"text": {"content": description}}]},
                "Fuente": {"rich_text": [{"text": {"content": job_data["Fuente"]}}]},
                "Fecha de Postulación": {
                    "date": {"start": current_date}  # Añadir la fecha actual
                },
                "Enlace": {"url": job_url}  # Añadir el enlace de la oferta
            }
        )
        return True
    return False

# Función para manejar la interfaz gráfica
def on_submit():
    url = url_entry.get()  # Obtener la URL ingresada
    
    if not url:
        result_label.config(text="Por favor ingrese una URL.", fg="red")
        return

    job_data = scrape_job_post(url)
    
    if job_data:
        success = add_to_notion(job_data, url)
        if success:
            result_label.config(text=f"Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", fg="green")
        else:
            result_label.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label.config(text="No se pudieron extraer los datos de la URL.", fg="red")
    
    # Limpiar el campo de entrada
    url_entry.delete(0, tk.END)

# Función para salir de la aplicación
def on_exit():
    root.quit()

import tkinter as tk
from tkinter import messagebox
from notion_client import Client
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Conectar con Notion
notion = Client(auth="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")

# ID de la base de datos de Notion
DATABASE_ID = "1927803780f880689fb6c59ee4469e13"

# Función para extraer datos de la URL
def scrape_job_post(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Intentar extraer el título (usando diferentes etiquetas y clases comunes)
        title = extract_title(soup)
        
        # Intentar extraer la compañía (usando diferentes etiquetas y clases comunes)
        company = extract_company(soup)
        
        # Intentar extraer la descripción (usando diferentes selectores comunes)
        description = extract_description(soup)
        
        Fuente = extract_fuente(soup)  # Añadir la URL de la oferta de empleo
        
        return {
            "Empresa": company,
            "Puesto": title,
            "Descripción": description,  # Añadir descripción
            "Fuente": Fuente  # Añadir la URL de la oferta
        }
    
    except Exception as e:
        print(f"Error al procesar la URL: {e}")
        return None

# Función para extraer el título del puesto
def extract_title(soup):
    title = soup.find(["h1", "h2", "h3"])  # Verifica h1, h2, h3 como posibles etiquetas
    if title:
        return title.get_text(strip=True)
    return "Título no encontrado"

# Función para extraer el nombre de la empresa
def extract_company(soup):
    company = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link")
    if company:
        return company.get_text(strip=True)
    return "Compañía no encontrada"

# Función para extraer la descripción del trabajo
def extract_description(soup):
    description = soup.find("div", class_="show-more-less-html__markup")  # Ajusta esta clase al selector correcto
    if description:
        return description.get_text(strip=True)
    return "Descripción no encontrada"

# Función para extraer la descripción del trabajo
def extract_fuente(soup):
    description = soup.find("span", class_="sr-only")  # Ajusta esta clase al selector correcto
    if description:
        return description.get_text(strip=True)
    return "fuente no encontrada"

# Función para enviar los datos a Notion
def add_to_notion(job_data, job_url):
    if job_data:
        # Limitar la longitud de la descripción a 2000 caracteres
        description = job_data["Descripción"]
        if len(description) > 2000:
            description = description[:2000]  # Cortar el texto si es mayor a 2000 caracteres
        
        # Obtener la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # Formato ISO 8601 para Notion
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Empresa": {"title": [{"text": {"content": job_data["Empresa"]}}]},
                "Puesto": {"rich_text": [{"text": {"content": job_data["Puesto"]}}]},
                "Descripción": {"rich_text": [{"text": {"content": description}}]},
                "Fuente": {"rich_text": [{"text": {"content": job_data["Fuente"]}}]},
                "Fecha de Postulación": {
                    "date": {"start": current_date}  # Añadir la fecha actual
                },
                "Enlace": {"url": job_url}  # Añadir el enlace de la oferta
            }
        )
        return True
    return False

# Función para manejar la interfaz gráfica
def on_submit():
    url = url_entry.get()  # Obtener la URL ingresada
    
    if not url:
        result_label.config(text="Por favor ingrese una URL.", fg="red")
        return

    job_data = scrape_job_post(url)
    
    if job_data:
        success = add_to_notion(job_data, url)
        if success:
            result_label.config(text=f"Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}", fg="green")
        else:
            result_label.config(text="No se pudo agregar la oferta a Notion.", fg="red")
    else:
        result_label.config(text="No se pudieron extraer los datos de la URL.", fg="red")
    
    # Limpiar el campo de entrada
    url_entry.delete(0, tk.END)

# Función para salir de la aplicación
def on_exit():
    root.quit()

# Configurar la ventana principal
root = tk.Tk()
root.title("Registrar Oferta de Empleo en Notion")
root.geometry("500x300")
root.configure(bg="#f5f5f7")  # Fondo gris claro similar a iCloud

# Estilo de fuente
font_style = ("Helvetica", 12)

# Etiqueta y campo de entrada para la URL
url_label = tk.Label(
    root,
    text="Introduce la URL de la oferta de empleo:",
    font=font_style,
    bg="#f5f5f7",  # Fondo gris claro
    fg="#1d1d1f"   # Texto oscuro
)
url_label.pack(pady=10)

url_entry = tk.Entry(
    root,
    width=40,
    font=font_style,
    bg="white",     # Fondo blanco
    fg="#1d1d1f",   # Texto oscuro
    relief=tk.FLAT,  # Sin borde
    borderwidth=0,
    highlightthickness=1,
    highlightbackground="#d2d2d7",  # Borde gris claro
    highlightcolor="#007aff"        # Borde azul al seleccionar
)
url_entry.pack(pady=5)

# Botón para procesar la URL (estilo iCloud)
submit_button = tk.Button(
    root,
    text="Agregar a Notion",
    command=on_submit,
    bg="#007aff",  # Azul iCloud
    fg="white",    # Texto blanco
    relief=tk.FLAT,  # Sin borde
    borderwidth=0,
    highlightthickness=0,
    padx=20,
    pady=10,
    font=font_style,
    activebackground="#0063cc",  # Azul más oscuro al hacer clic
    activeforeground="white"
)
submit_button.pack(pady=10)

# Etiqueta para mostrar los resultados
result_label = tk.Label(
    root,
    text="",
    font=font_style,
    wraplength=400,
    bg="#f5f5f7",  # Fondo gris claro
    fg="#1d1d1f"   # Texto oscuro
)
result_label.pack(pady=10)

# Botón de salir (estilo iCloud)
exit_button = tk.Button(
    root,
    text="Salir",
    command=on_exit,
    bg="#ff3b30",  # Rojo iCloud
    fg="white",    # Texto blanco
    relief=tk.FLAT,  # Sin borde
    borderwidth=0,
    highlightthickness=0,
    padx=20,
    pady=10,
    font=font_style,
    activebackground="#cc2b24",  # Rojo más oscuro al hacer clic
    activeforeground="white"
)
exit_button.pack(pady=10)

# Iniciar la interfaz gráfica
root.mainloop()