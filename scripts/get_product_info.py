from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json

# Inicia o navegador Edge e abre o site da Nissei
driver = webdriver.Edge()
driver.get('https://www.farmaciasnissei.com.br/')

# Lista para armazenar os dados dos produtos extraídos
extracted_products = []

# Lê o arquivo com os EAMs, um por linha
with open('eam_list.txt', 'r', encoding='utf-8') as arquivo:
    for eam in arquivo:
        try:
            eam = eam.strip()  # Remove espaços e quebras de linha

            # Aguarda o campo de busca estar clicável e envia o EAM
            search_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'barra-pesquisa'))
            )
            search_input.clear()
            search_input.send_keys(eam)
            search_input.send_keys(Keys.ENTER)

            # Aguarda o carregamento da grade de produtos e clica no primeiro item
            product_grid = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'grade_produtos'))
            )
            product = product_grid.find_element(By.XPATH, './div[1]')
            product.click()

            # Aguarda os detalhes do produto aparecerem
            product_info = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, './/div[@data-target="produto_view"]'))
            )

            # Captura o EAM apresentado no site para verificação
            extracted_eam = product_info.find_element(By.XPATH, './/span[@class="mr-3"]')

            if eam in extracted_eam.text:
                # Extrai os dados do produto
                internal_code = product_info.find_element(By.XPATH, './/span[@class="ml-3"]').text.replace('Código:', '').strip()
                name = product_info.find_element(By.XPATH, './/h1[@data-target="nome_produto"]').text.strip()
                image_src = driver.find_element(By.CLASS_NAME, 'img-zoom-produto').get_attribute('src')

                # Armazena os dados formatados
                extracted_products.append({
                    "eam": eam,
                    "codigo": internal_code,
                    "nome": name,
                    "imagem": image_src
                })
            else:
                # O EAM retornado não corresponde ao buscado
                extracted_products.append({
                    "eam": eam,
                    "eam_site": extracted_eam.text,
                    "erro": "EAM diferente do que está registrado no site"
                })
        except Exception as e:
            # Registra qualquer erro ocorrido durante a extração
            extracted_products.append({
                "eam": eam,
                "erro": str(e)
            })

# Exporta os dados para um arquivo .txt no formato separado por ponto e vírgula
with open('produtos_formatado.txt', 'w', encoding='utf-8') as p_txt:
    for product in extracted_products:
        if 'erro' in product:
            p_txt.write(f"{product['eam']};{product['erro']}\n")
        else:
            p_txt.write(f"{product['eam']};{product['codigo']};{product['nome']};{product['imagem']}\n")

# Salva os dados estruturados em JSON
with open('produtos.json', 'w', encoding='utf-8') as p_json:
    json.dump(extracted_products, p_json, ensure_ascii=False, indent=4)

# Fecha o navegador
driver.quit()
