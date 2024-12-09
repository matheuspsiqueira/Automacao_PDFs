import fitz  
import re
import pytesseract
from PIL import Image
import io
import os, sys
import shutil
import subprocess
import requests

def instalar_chocolatey():
    if not os.path.exists(r'C:\ProgramData\chocolatey'):
        print("Instalando Chocolatey...")
        subprocess.run(
            ['powershell', '-NoProfile', '-InputFormat', 'None', '-ExecutionPolicy', 'Bypass', 
             '-Command', 
             'Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString("https://chocolatey.org/install.ps1"))'],
            check=True
        )
        print("Chocolatey instalado com sucesso.")

def instalar_tesseract():
    try:
        print("Instalando Tesseract...")
        subprocess.run(['choco', 'install', 'tesseract', '-y'], check=True)
        print("Tesseract instalado com sucesso.")
    except FileNotFoundError as e:
        print(f"Erro ao tentar instalar Tesseract: {e}")

def baixar_traineddata():
    caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tessdata"
    os.makedirs(caminho_tesseract, exist_ok=True)
    url = "https://github.com/tesseract-ocr/tessdata/raw/master/por.traineddata"
    caminho_arquivo = os.path.join(caminho_tesseract, "por.traineddata")

    if not os.path.exists(caminho_arquivo):
        print("Baixando o arquivo por.traineddata...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(caminho_arquivo, 'wb') as f:
                f.write(response.content)
            print("Arquivo por.traineddata baixado com sucesso.")
        else:
            print(f"Falha ao baixar por.traineddata: {response.status_code}")

def definir_variaveis_ambiente():
    os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR"
    print("TESSDATA_PREFIX definido.")

def verificar_instalacao():
    try:
        subprocess.run(['tesseract', '--version'], check=True)
    except FileNotFoundError:
        print("Tesseract não encontrado. Instalando Chocolatey e Tesseract...")
        instalar_chocolatey()
        instalar_tesseract()
        baixar_traineddata()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar Tesseract: {e}")

def adicionar_tesseract_ao_path():
    caminho_tesseract = r"C:\Program Files\Tesseract-OCR"
    if caminho_tesseract not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + caminho_tesseract
        print(f"{caminho_tesseract} adicionado ao PATH.")
    else:
        print(f"{caminho_tesseract} já está no PATH.")

def obter_caminho_tesseract():
    if getattr(sys, 'frozen', False):
        caminho_tesseract = os.path.join(sys._MEIPASS, "tesseract.exe")
    else:
        caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    if os.path.exists(caminho_tesseract):
        return caminho_tesseract
    else:
        raise FileNotFoundError("Tesseract não encontrado em " + caminho_tesseract)

def configurar_tesseract():
    adicionar_tesseract_ao_path()
    
    pytesseract.pytesseract.tesseract_cmd = obter_caminho_tesseract()
    
    if getattr(sys, 'frozen', False):
        tessdata_path = os.path.join(sys._MEIPASS, "tessdata")
    else:
        tessdata_path = r"C:\Program Files\Tesseract-OCR\tessdata"
    
    os.environ['TESSDATA_PREFIX'] = tessdata_path
    print(f"TESSDATA_PREFIX definido como: {tessdata_path}")

try:
    verificar_instalacao()
    adicionar_tesseract_ao_path()
    definir_variaveis_ambiente()
    configurar_tesseract()
    pytesseract.pytesseract.tesseract_cmd = obter_caminho_tesseract()
except Exception as e:
    print(f"Ocorreu um erro: {e}")
    sys.exit(1)  

def extrair_titulos_e_agrupamento_pdf(arquivo_pdf, pasta_saida):
    try:
        documento = fitz.open(arquivo_pdf)
        print(f"PDF '{arquivo_pdf}' aberto. Páginas: {documento.page_count}")
    except Exception as e:
        print(f"Erro ao abrir o PDF: {e}")
        return

    padrao_fa = r'\bFA-\d{3}\b'
    padrao_titulo = r'^[A-ZÀ-Ú ]{5,}$'
    grupos = {}

    def salvar_grupos():
        """Salva PDFs separados por grupos."""
        for nome_grupo, paginas in grupos.items():
            pdf = fitz.open()
            for pagina in paginas:
                pdf.insert_pdf(documento, from_page=pagina, to_page=pagina)
            nome_arquivo = f"{nome_grupo.replace(' ', '_')}.pdf"
            caminho_arquivo = os.path.join(pasta_saida, nome_arquivo)

            try:
                pdf.save(caminho_arquivo)
                print(f"PDF '{nome_arquivo}' salvo em '{pasta_saida}'.")
            except Exception as e:
                print(f"Erro ao salvar PDF '{nome_arquivo}': {e}")
            finally:
                pdf.close()  

    def eh_titulo_valido(titulo):
        return (titulo.isupper() and "_" not in titulo and "-" not in titulo)

    for num_pagina in range(documento.page_count):
        print(f"Lendo página {num_pagina + 1}...")
        pagina = documento.load_page(num_pagina)
        texto = pagina.get_text("text")

        if not texto.strip():
            print("Página vazia. Usando OCR...")
            img = pagina.get_pixmap()
            imagem = Image.open(io.BytesIO(img.tobytes("png")))
            texto = pytesseract.image_to_string(imagem, lang='por')

        fa_encontrado = re.search(padrao_fa, texto)
        nome_grupo = fa_encontrado.group() if fa_encontrado else None

        if not nome_grupo:
            titulo_encontrado = re.search(padrao_titulo, texto, re.MULTILINE)
            if titulo_encontrado and eh_titulo_valido(titulo_encontrado.group()):
                nome_grupo = titulo_encontrado.group().strip()

        if nome_grupo:
            grupos.setdefault(nome_grupo, []).append(num_pagina)

    salvar_grupos()
    documento.close()

    try:
        shutil.move(arquivo_pdf, os.path.join(pasta_saida, os.path.basename(arquivo_pdf)))
        print(f"PDF original movido para '{pasta_saida}'.")
    except Exception as e:
        print(f"Erro ao mover PDF: {e}")

    print("Processamento concluído.")

def processar_pdfs_na_pasta(pasta_entrada):
    """Processa todos os PDFs da pasta de entrada."""
    for arquivo in os.listdir(pasta_entrada):
        if arquivo.endswith('.pdf'):
            caminho_pdf = os.path.join(pasta_entrada, arquivo)
            pasta_saida = os.path.join(pasta_entrada, os.path.splitext(arquivo)[0])
            os.makedirs(pasta_saida, exist_ok=True)
            extrair_titulos_e_agrupamento_pdf(caminho_pdf, pasta_saida)

if __name__ == "__main__":
    processar_pdfs_na_pasta("./")
