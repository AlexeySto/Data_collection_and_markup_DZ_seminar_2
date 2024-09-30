import requests
from bs4 import BeautifulSoup
import re
import csv
import json

def fetch_vacancies(profession):
    vacancies = []
    
    url = 'https://hh.ru/search/vacancy?hhtmFrom=main&hhtmFromLabel=vacancy_search_line&search_field=name&search_field=description&search_field=company_name&enable_snippets=false&L_save_area=true&text={}&page={}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    session = requests.session()
    page_number = 1
    count_jobs = 1
    while True:
        response = requests.get(url.format(profession.replace(' ', '+'), page_number), headers=headers)
        if response.status_code > 399 :
            print("Ответ от сервера не получен.")
            print(f"Код ответа: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup:
            break

        for item in soup.find_all('div', {'class': 'magritte-redesign'}):
            job = {}
            job['title'] = item.find('span', {'data-qa': 'serp-item__title-text'}).getText()
            salary = salary_split(item.find('span', {'class': 'magritte-text_typography-label-1-regular___pi3R-_3-0-15'}))
            job['salary_from'] = salary['salary_from']
            job['salary_to'] = salary['salary_to']                   
            vacancies.append(job)
            print('Добавлено вакансий: ' + str(count_jobs))
            count_jobs += 1
        
        page_number += 1
            
    return vacancies

def salary_split(salary):
    if salary != None:
        salary_text = salary.getText().strip().replace('\u202f', '')
        salary_parts = salary_text.split('–')
        if len(salary_parts) > 1:
            salary_from = extract_number(salary_parts[0])
            salary_to = extract_number(salary_parts[1])
        else:
            salary_parts = salary_text.split()
            if salary_parts[0] == 'от':
                salary_from = extract_number(salary_text)
                salary_to = None
            else:
                salary_from = None
                salary_to = extract_number(salary_text)
    else:
        salary_from = None
        salary_to = None
            
    return {'salary_from' : salary_from, 'salary_to' : salary_to}  
      
def extract_number(string):
    # Ищем в строке все цифры, а затем конвертируем в целое число
    match = re.search(r'\d+', string)
    if match:
        return int(match.group())
    return None  # Вернуть None, если число не найдено
                
def save_to_csv(vacancies, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'salary_from', 'salary_to'])
        writer.writeheader()
        writer.writerows(vacancies)

def save_to_json(vacancies, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(vacancies, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    profession = input("Введите название профессии: ")
    vacancies = fetch_vacancies(profession)
    
    if len(vacancies) != 0:
        save_to_csv(vacancies, 'vacancies.csv')
        save_to_json(vacancies, 'vacancies.json')

        print(f"Найдено вакансий: {len(vacancies)}")
        print("Данные сохранены в файлы vacancies.csv и vacancies.json.")
    else:
        print("Не нашлось ни одной вакансии.")
    