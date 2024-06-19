import requests
from bs4 import BeautifulSoup
import re
import os
import uuid
import urllib.parse
from DBConn import insert_product
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

folder_path = 'F://PycharmProjects/cosmetic/photo'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
catalog_url = 'https://bbcream.ru/dekorativnaya-kosmetika/dlya-gub/pomada/page-2/'
response = requests.get(catalog_url)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
product_cards = soup.find_all('div', class_='ty-column3')

if not product_cards:
    print("не удалось найти карточки товаров.")
else:
    products = []
    for product_card in product_cards:
        link = product_card.find('a', href=True)
        if link and 'href' in link.attrs:
            href = link['href']
            if href.startswith('https://'):
                product_url = href
            else:
                product_url = 'https://bbcream.ru' + href

            try:
                product_response = requests.get(product_url)
                product_html_content = product_response.text
                product_soup = BeautifulSoup(product_html_content, 'html.parser')

                title_element = product_soup.find('span', class_='ty-product-block-title_deck')
                title = title_element.text.strip() if title_element else "не найдено"

                price_element = product_soup.find('span', class_='ty-price')
                price = price_element.text.strip() if price_element else "не найдено"

                brand_element = product_soup.find('label', class_='header_list__features-list-item')
                brand = brand_element.text.strip() if brand_element else "не найдено"

                color_element = product_soup.find('div', class_='ty-product-option-child')
                color = color_element.text.strip() if color_element else "не найдено"

                category_element = product_soup.find('span', class_='ty-block ty-product-block-title inverse')
                category = category_element.text.strip() if category_element else "не найдено"

                weight_element = product_soup.find('select', class_='cm-history cm-ajax-force')
                weight = weight_element.text.strip() if weight_element else "не найдено"

                elements = product_soup.find_all('span', class_='ty-product-feature__desc')
                if elements:
                    last_element = elements[-1]
                    country = last_element.text.strip()
                    country = country.replace(";", "").strip()
                else:
                    country = "не найдено"

                struct_element = product_soup.find('div', id='content_note')

                if struct_element:
                    struct_text = struct_element.get_text().strip()
                else:
                    struct_text = "не найдено"

                desc_element = product_soup.find('div', id='content_description')
                if desc_element:
                    desc_text = desc_element.get_text().strip()

                    desc_lines = desc_text.splitlines()

                    start_index = 0
                    for i, line in enumerate(desc_lines):
                        if 'Страна производства:' in line:
                            start_index = i + 3
                            break
                    desc_lines = desc_lines[start_index:]

                    application_index = None
                    for i, line in enumerate(desc_lines):
                        if 'Способ применения:' in line:
                            application_index = i
                            break

                    if application_index is not None:
                        description = '\n'.join(desc_lines[:application_index]).strip()
                        application = '\n'.join(desc_lines[application_index:]).strip()

                        application = application.replace('Способ применения:', '').strip()
                    else:
                        description = '\n'.join(desc_lines).strip()
                        application = "не найдено"
                else:
                    description = "не найдено"
                    application = "не найдено"

                product_info = {
                    "Название": title,
                    "Цена": price,
                    "Оттенок": color,
                    "Бренд": brand,
                    "Категория": category,
                    "Вес": weight,
                    "Страна": country,
                    "Описание": description,
                    "Способ применения": application,
                    "Состав": struct_text
                }

                products.append(product_info)
                image_carousel = product_soup.find('div', class_='ty-product-bigpicture__left-wrapper')

                if image_carousel:
                    image_elements = image_carousel.find_all('img')
                    for index, image_element in enumerate(image_elements):
                        if image_element and 'src' in image_element.attrs:
                            existing_files = os.listdir(folder_path)

                            existing_image_numbers = [int(file.split('.')[0]) for file in existing_files if
                                                      file.endswith('.jpg')]

                            last_image_number = max(existing_image_numbers) if existing_image_numbers else 0

                            new_image_number = last_image_number + 1
                            image_url = image_element['src']
                            file_name = f"{new_image_number}.jpg"
                            download_image(image_url, folder_path, file_name)
                            break
                        else:
                            print("не найдено")
                else:
                    print("карусель не найдена")


            except requests.ConnectionError as e:
                print(f"ошибка соединения для URL: {product_url}")
                print(str(e))

            type = "Товары для губ"
            insert_product(file_name, title, category, weight, country,
                               description, application, struct_text,
                               color, price, brand, type)
        else:
            print("ссылка не найдена в карточке товара:", product_card)

    # for product in products:
    #     print("Название:", product["Название"])
    #     print("Цена:", product["Цена"])
    #     print("Оттенок:", product["Оттенок"])
    #     print("Бренд:", product["Бренд"])
    #     print("Категория:", product["Категория"])
    #     print("Вес:", product["Вес"])
    #     print("Страна:", product["Страна"])
    #     print("Описание:", product["Описание"])
    #     print("Способ применения:", product["Способ применения"])
    #     print("Состав:", product["Состав"])