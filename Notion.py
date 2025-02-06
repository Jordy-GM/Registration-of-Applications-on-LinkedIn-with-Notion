from notion_client import Client
import requests
from bs4 import BeautifulSoup

# Conectar con Notion
notion = Client(auth="TU_TOKEN_DE_IN")

# ID de la base de datos de Notion
DATABASE_ID = "tu_id_de_base_de_datos"

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
        
        print("Datos extraídos:")
        print(f"Título: {title}")
        print(f"Compañía: {company}")
        print(f"Descripción: {description}")
        print(f"Fuente: {Fuente}")
        
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
def add_to_notion(job_data):
    if job_data:
        # Limitar la longitud de la descripción a 2000 caracteres
        description = job_data["Descripción"]
        if len(description) > 2000:
            description = description[:2000]  # Cortar el texto si es mayor a 2000 caracteres
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Empresa": {"title": [{"text": {"content": job_data["Empresa"]}}]},
                "Puesto": {"rich_text": [{"text": {"content": job_data["Puesto"]}}]},
                "Descripción": {"rich_text": [{"text": {"content": description}}]},
                "Fuente": {"rich_text": [{"text": {"content": job_data["Fuente"]}}]}
            }
        )
        print(f"Oferta agregada: {job_data['Puesto']} en {job_data['Empresa']}")

# Función para pedir la URL al usuario y procesar múltiples URLs
def process_job_posts():
    while True:
        url = input("Introduce la URL de la oferta de empleo (o escribe 'salir' para terminar): ")
        
        if url.lower() == 'salir':
            print("Proceso finalizado.")
            break
        
        job_data = scrape_job_post(url)
        
        if job_data:
            add_to_notion(job_data)

# Ejecutar el proceso
process_job_posts()
