import requests
from bs4 import BeautifulSoup
import re
import os
import urllib.parse
from DBConn import insert_product

def split_text_block(text_block, description_block):
    keys = ['Область использования', 'Вес в упаковке', 'Текстура', 'Высота упаковки', 'Ширина упаковки',
            'Длина упаковки', 'Тег', 'Раздел', 'Артикул', 'Страна', 'Способ применения', 'Состав']
    pattern = '|'.join([f'{key}:' for key in keys])
    parts = re.split(f'({pattern})', text_block)
    info_dict = {}
    current_key = None
    description = ""
    is_description = False
    description_started = False

    for part in parts:
        part = part.strip()
        if part.endswith(':'):
            current_key = part[:-1].strip()
            if current_key == "Страна":
                description_started = True
            if current_key == "Способ применения":
                is_description = False
                description_started = False
        elif current_key:
            info_dict[current_key] = part
            current_key = None
        elif description_started:
            description += part + " "

    description += description_block
    description = description.strip().replace("Все товары бренда", "").strip()
    info_dict['Описание'] = description

    country_match = re.search(r'Страна:\s*([\w\s]+)', text_block)
    country = country_match.group(1) if country_match else "не найдено"
    info_dict['Страна'] = country.strip()

    return info_dict

def download_image(url, folder_path, file_name):
    full_url = urllib.parse.urljoin('https://www.m.podrygka.ru', url)
    response = requests.get(full_url)
    if response.status_code == 200:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"изображение сохранено как {file_name}")
    else:
        print(f"не удалось скачать изображение с URL: {url}")

catalog_url = 'https://www.m.podrygka.ru/catalog/makiyazh/brovi/tush_dlya_brovei/'
response = requests.get(catalog_url)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
product_cards = soup.find_all('div', class_='item-product-card')
folder_path = 'F://PycharmProjects/cosmetic/photo'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

if not product_cards:
    print("не удалось найти карточки товаров.")
else:
    for product_card in product_cards:
        link = product_card.find('a', href=True)
        if not link or 'href' not in link.attrs:
            print("ссылка не найдена в карточке товара:", product_card)
            continue

        product_url = 'https://www.m.podrygka.ru' + link['href']
        product_response = requests.get(product_url)
        product_html_content = product_response.text
        product_soup = BeautifulSoup(product_html_content, 'html.parser')

        text_block_element = product_soup.find('div', class_='tabs-content-toggle')
        description_block_element = product_soup.find('div', class_='__text')
        text_block = text_block_element.text if text_block_element else ""
        description_block = description_block_element.text if description_block_element else ""
        info_dict = split_text_block(text_block, description_block)

        title_element = product_soup.find('div', class_='product-detail__desc')
        title = title_element.text.strip() if title_element else "не найдено"

        if title == "не найдено":
            print("Название товара не найдено:", product_url)
            continue

        price_element = product_soup.find('span', class_='product-detail-price-wrapper__price__current-price')
        price = price_element.text.strip() if price_element else "не найдено"

        name_section = product_soup.find('div', class_='page-block-title center_options left_in_box')
        name_text = name_section.text if name_section else ""
        tonal_info = re.search(r'ТОН (\d+)', name_text)
        tonal_number = tonal_info.group(1) if tonal_info else "не найдено"

        usage_area = info_dict.get('Область использования', "не найдено")
        weight = info_dict.get('Вес в упаковке', "не найдено")
        texture = info_dict.get('Текстура', "не найдено")
        height = info_dict.get('Высота упаковки', "не найдено")
        width = info_dict.get('Ширина упаковки', "не найдено")
        length = info_dict.get('Длина упаковки', "не найдено")
        tag = info_dict.get('Тег', "не найдено")
        section = info_dict.get('Раздел', "не найдено")
        article = info_dict.get('Артикул', "не найдено")
        country = info_dict.get('Страна', "не найдено")
        description = info_dict.get('Описание', "не найдено")
        application_method = info_dict.get('Способ применения', "не найдено")
        composition = info_dict.get('Состав', "не найдено")

        image_carousel = product_soup.find('div', class_='product-detail__gallery')
        file_name = "не найдено"

        if image_carousel:
            image_elements = image_carousel.find_all('img')
            for index, image_element in enumerate(image_elements):
                if image_element and 'src' in image_element.attrs:
                    existing_files = os.listdir(folder_path)
                    existing_image_numbers = [int(file.split('.')[0]) for file in existing_files if file.endswith('.jpg')]
                    last_image_number = max(existing_image_numbers) if existing_image_numbers else 0
                    new_image_number = last_image_number + 1
                    image_url = image_element['src']
                    file_name = f"{new_image_number}.jpg"
                    download_image(image_url, folder_path, file_name)
                    break
            else:
                print("не найдено", product_url)
                continue
        else:
            print("Карусель не найдена:", product_url)
            continue

        type = "Товары для бровей"
        insert_product(file_name, title, texture, weight, country, description, application_method, composition, tonal_number, price, "не найдено", type)