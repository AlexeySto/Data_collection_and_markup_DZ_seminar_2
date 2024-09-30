import requests
from bs4 import BeautifulSoup
import json
import re


# Функция для получения информации о книге
def get_book_info(book):
    title = book.h3.a['title']
    price = float(book.find('p', class_='price_color').text[2:])
    link = book.h3.a['href']
    
    # Получение описания книги
    book_detail_url = base_url + f"{link}"
    detail_response = requests.get(book_detail_url)
    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
    availability = extract_number(detail_soup.find('p', {'class': 'instock'}).getText())
    description = detail_soup.find('meta', attrs={'name': 'description'})['content'].strip()
    
    return {
        'title': title,
        'price': price,
        'availability': availability,
        'description': description
    }

def extract_number(string):
    # Ищем в строке все цифры, а затем конвертируем в целое число
    match = re.search(r'\d+', string)
    if match:
        return int(match.group())
    return None  # Вернуть None, если число не найдено


if __name__ == '__main__':
    # URL страницы с книгами
    base_url = "http://books.toscrape.com/catalogue/"
    additional_url = "page-{}.html"
    
    # Список для хранения информации о книгах
    books_data = []

    # Перебор страниц
    page_number = 1
    count_books = 1
    while True:
        response = requests.get(base_url + additional_url.format(page_number))
        if response.status_code > 399 :
            print("Ответ от сервера не получен.")
            print(f"Код ответа: {response.status_code}")
            break
    
        soup = BeautifulSoup(response.text, 'html.parser')

        # Найти все книги на странице
        books = soup.find_all('article', class_='product_pod')

        if not books:
            break  # Выход из цикла, если книги не найдены

        for book in books:
            book_info = get_book_info(book)
            books_data.append(book_info)
            print('Добавлена книга: ' + str(count_books))
            count_books += 1

        page_number += 1

    if len(books_data) != 0:
        # Сохранение данных в JSON файл
        with open('books.json', 'w', encoding='utf-8') as json_file:
            json.dump(books_data, json_file, ensure_ascii=False, indent=4)

        print(f"Собрано {len(books_data)} книг. Данные сохранены в 'books.json'.")
    else:
        print("Не нашлось ни одной книги.")
