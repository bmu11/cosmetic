import requests
from bs4 import BeautifulSoup
import re
import os
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

catalog_url = 'https://chudodey.com/async_catalog/guby/karandashi-dlya-gub/filters/filter12/filter_type/SG/filters/filter12/filter_name/в%20наличии%20и%20под%20заказ/filters/filter12/values/sort/field_name/title/sort/sort_type/возрастание/pager/page_number/1'
response = requests.get(catalog_url)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
product_cards = soup.find_all('div', class_='p-0 px-md-2 col-6 col-lg-4 has-divider')

if not product_cards:
    print("не удалось найти карточки товаров.")
else:
    print(f"найдено {len(product_cards)} товаров.")

    for card in product_cards:
        link = card.find('a', href=True)
        if link and 'href' in link.attrs:
            product_url = link['href']
            product_response = requests.get(product_url)
            product_html_content = product_response.text
            product_soup = BeautifulSoup(product_html_content, 'html.parser')

            title_element = product_soup.find('h1', class_='product-detail__header')
            title = title_element.text.strip() if title_element else "не найдено"

            price_element = product_soup.find('div', class_='product-detail__price')
            price = price_element.text.strip() if price_element else "не найдено"

            tab_pane_inner = product_soup.find('div', class_='tab-pane__inner')
            if tab_pane_inner:
                tab_text = tab_pane_inner.get_text(separator="\n").strip()
                description_start = tab_text.find('Описание')
                ingredients_start = tab_text.find('Состав:')
                if description_start != -1 and ingredients_start != -1:
                    description = tab_text[description_start + len('Описание:'):ingredients_start].strip()
                    ingredients = tab_text[ingredients_start + len('Состав:'):].strip()
                else:
                    description = "не найдено"
                    ingredients = "не найдено"
            else:
                description = "не найдено"
                ingredients = "не найден"

            elements = product_soup.find_all('dd', class_='col-7')
            country = "не найдено"
            weight = "не найдено"
            color = "не найдено"
            category = "не найдено"
            brand = "не найдено"

            if len(elements) >= 6:
                weight = elements[0].text.strip()
                color = elements[1].text.strip()
                category = elements[2].text.strip()
                brand = elements[4].text.strip()
                country = elements[5].text.strip()
            elif len(elements) >= 5:
                weight = elements[0].text.strip()
                color = elements[1].text.strip()
                category = elements[2].text.strip()
                brand = elements[3].text.strip()
            elif len(elements) >= 4:
                weight = elements[0].text.strip()
                color = elements[1].text.strip()
                category = elements[2].text.strip()
            elif len(elements) >= 3:
                weight = elements[0].text.strip()
                color = elements[1].text.strip()
                category = elements[2].text.strip()
            elif len(elements) >= 2:
                weight = elements[0].text.strip()
                color = elements[1].text.strip()
            elif len(elements) >= 1:
                weight = elements[0].text.strip()

            # print("Название:", title)
            # print("Оттенок:", color)
            # print("Объем:", weight)
            # print("Категория:", category)
            # print("Цена:", price)
            # print("Страна:", country)
            # print("Бренд:", brand)
            # print("Описание:", description)
            # print("Состав:", ingredients)

            image_element = product_soup.find(id='product-image')
            if image_element:
                image_url = image_element.get('src') or image_element.get('data-src')
                if image_url:
                    existing_files = os.listdir(folder_path)
                    existing_image_numbers = [int(file.split('.')[0]) for file in existing_files if file.endswith('.jpg')]
                    last_image_number = max(existing_image_numbers) if existing_image_numbers else 0
                    new_image_number = last_image_number + 1
                    file_name = f"{new_image_number}.jpg"
                    download_image(image_url, folder_path, file_name)
                else:
                    print("URL изображения не найден")
            else:
                print("изображение с id 'product-image' не найдено")
                file_name = "не найдено"

            type = "Товары для губ"
            insert_product(file_name, title, category, weight, country,
                           description, "не найдено", ingredients,
                           color, price, brand, type)
        else:
            print("ссылка не найдена в карточке товара:", card)