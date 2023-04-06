import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import List


class VorHTML:
    def __init__(self, url):
        self.url = url

    def save_file(self, url, path):
        response = requests.get(url)
        with open(path, 'wb') as f:
            f.write(response.content)

    def save_html(self, path):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # сохраняем все изображения
        for img in soup.find_all('img'):
            img_url = urljoin(self.url, img.get('src'))
            img_path = os.path.join(path, os.path.basename(urlparse(img_url).path))
            self.save_file(img_url, img_path)

        # сохраняем CSS и JavaScript файлы
        for link in soup.find_all('link'):
            if link.get('href') and link.get('href').endswith(('.css', '.js')):
                file_url = urljoin(self.url, link.get('href'))
                file_path = os.path.join(path, os.path.basename(urlparse(file_url).path))
                self.save_file(file_url, file_path)

        # сохраняем все ссылки на файлы
        for link in soup.find_all('a'):
            if link.get('href') and link.get('href').endswith(('.css', '.js')):
                file_url = urljoin(self.url, link.get('href'))
                file_path = os.path.join(path, os.path.basename(urlparse(file_url).path))
                self.save_file(file_url, file_path)

        # сохраняем HTML-файл
        html_path = os.path.join(path, 'index.html')
        with open(html_path, 'wb') as f:
            f.write(response.content)

        print('Все файлы сохранены в папку:', path)

    def check_file_exists(self, path):
        if os.path.exists(path):
            print('Файл существует')
        else:
            print('Файл не существует')


class VorHTMLMerger:
    def __init__(self, file_paths: List[str], output_path: str):
        self.file_paths = file_paths
        self.output_path = output_path

    def merge_files(self):
        soup = BeautifulSoup(features='html.parser')
        head = soup.new_tag('head')
        body = soup.new_tag('body')
        soup.append(head)
        soup.append(body)

        for path in self.file_paths:
            with open(path, 'rb') as f:
                file_soup = BeautifulSoup(f.read(), features='html.parser')
                if file_soup.head:
                    head.append(file_soup.head)
                if file_soup.body:
                    body.append(file_soup.body)

        with open(self.output_path, 'wb') as f:
            f.write(soup.encode())
            print('Файлы успешно объединены в', self.output_path)

if __name__ == '__main__':
    path = input('Введите путь сохранения: ').strip()
    if not os.path.exists(path):
        os.makedirs(path)
    site_url = input('Введите адрес сайта: ').strip()

    scraper = VorHTML(site_url)
    scraper.save_html(path)
    scraper.check_file_exists(path)

    # объединяем HTML-файлы в один
    html_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.html')]
    output_file = os.path.join(path, 'merged.html')
    merger = VorHTMLMerger(html_files, output_file)
    merger.merge_files()