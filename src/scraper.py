from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import json
import os

def capturar_dados_dashboard(empresa='kabum'):
    chrome_options = Options()
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    
    if os.path.exists("/usr/bin/chromedriver"):
        service = Service(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    url = f"https://www.reclameaqui.com.br/empresa/{empresa}/"
    
    try:
        driver.get(url)
        time.sleep(5) 

        spans = driver.find_elements(By.TAG_NAME, 'span')
        
        texto_completo = [s.text for s in spans if s.text]
        
        def extrair(termo):
            for t in texto_completo:
                if termo in t:
                    return t
            return "N/A"

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        resultado_bruto = {
            "empresa": empresa,
            "data_coleta": timestamp,
            "Total Reclamações": extrair("recebeu"),
            "Respondidas": extrair("Respondeu"),
            "Aguardando": extrair("aguardando resposta"),
            "Nota Média": extrair("nota média"),
            "Voltariam a Negociar": extrair("voltariam a fazer negócio"),
            "Índice de Solução": extrair("resolveu"),
            "Tempo Médio": extrair("tempo médio de resposta")
        }
        
        if not os.path.exists('data/bronze'):
            os.makedirs('data/bronze')

        caminho_arquivo = f'data/bronze/dashboard_{empresa}_{resultado_bruto['data_coleta']}.json'
        with open(caminho_arquivo, 'w', encoding='utf8') as f:
            json.dump(resultado_bruto, f, ensure_ascii=False, indent=4)

        return resultado_bruto
    except Exception as e:
        return {"erro": str(e)}
    finally:

        driver.quit()


