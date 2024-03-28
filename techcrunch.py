"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time

import dateparser
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from src.spp.types import SPP_document
from datetime import datetime
import pytz
from random import uniform


class Techсrunch:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'techcrunch'
    HOST = "https://techcrunch.com/category/fintech/"
    _content_document: list[SPP_document]
    utc = pytz.UTC

    def __init__(self, webdriver, max_count_documents: int = None, last_document: SPP_document = None, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []
        self._driver = webdriver
        self._max_count_documents = max_count_documents
        self._last_document = last_document
        self._wait = WebDriverWait(self._driver, timeout=20)

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        try:
            self._parse()
        except Exception as e:
            self.logger.debug(f'Parsing stopped with error: {e}')
        else:
            self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        self._initial_access_source("https://techcrunch.com/category/fintech/")
        self._wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '.river')))
        time.sleep(3)
        while True:

            self.logger.debug('Загрузка списка элементов...')
            doc_table = self._driver.find_element(By.CLASS_NAME, 'river').find_elements(By.XPATH,
                                                                                       '//article[contains(@class,\'post-block\')]')
            self.logger.debug('Обработка списка элементов...')

            for i, element in enumerate(doc_table):
                try:
                    title = doc_table[i].find_element(By.XPATH,
                                                      './/a[contains(@class,\'post-block__title__link\')]').text
                except:
                    self.logger.exception('Не удалось извлечь title')
                    continue
                other_data = None

                try:
                    abstract = doc_table[i].find_element(By.CLASS_NAME, 'post-block__content').text
                except:
                    self.logger.exception('Не удалось извлечь abstract')
                    abstract = None

                try:
                    web_link = doc_table[i].find_element(By.XPATH,
                                                         './/*[contains(@class,\'post-block__title\')]').find_element(
                        By.TAG_NAME, 'a').get_attribute('href')
                except:
                    self.logger.exception('Не удалось извлечь web_link, пропущен')
                    continue

                self._driver.execute_script("window.open('');")
                self._driver.switch_to.window(self._driver.window_handles[1])
                self._driver.get(web_link)
                time.sleep(5)
                try:
                    pub_date = self.utc.localize(
                        dateparser.parse(self._driver.find_element(By.XPATH,
                                                                  '//time[contains(@class, \'full-date-time\')]').get_attribute(
                            'datetime')))
                except:
                    self.logger.exception('Не удалось извлечь pub_date')
                    continue

                try:
                    text_content = self._driver.find_element(By.XPATH,
                                                            '//div[contains(@class, \'article-content\')]').text
                except:
                    self.logger.exception('Не удалось извлечь text_content')
                    text_content = None

                document = SPP_document(
                    id=None,
                    title=title,
                    abstract=abstract,
                    text=text_content,
                    web_link=web_link,
                    local_link=None,
                    other_data=other_data,
                    pub_date=pub_date,
                    load_date=None,
                )
                self.find_document(document)
                self._driver.close()
                self._driver.switch_to.window(self._driver.window_handles[0])

            try:
                # // *[ @ id = "all-materials"] / font[2] / a[5]
                pagination_arrow = self._driver.find_element(By.XPATH, '//*[@id="all-materials"]/font[2]/a[5]')
                pg_num = pagination_arrow.get_attribute('href')
                self._driver.execute_script('arguments[0].click()', pagination_arrow)
                time.sleep(3)
                self.logger.info(f'Выполнен переход на след. страницу: {pg_num}')
            except:
                raise NoSuchElementException('Не удалось найти переход на след. страницу. Прерывание цикла обработки')

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    def _initial_access_source(self, url: str, delay: int = 2):
        self._driver.get(url)
        self.logger.debug('Entered on web page ' + url)
        time.sleep(delay)
        self._agree_cookie_pass()

    def _agree_cookie_pass(self):
        """
        Метод прожимает кнопку agree на модальном окне
        """
        cookie_agree_xpath = '//*[@id="onetrust-accept-btn-handler"]'

        try:
            cookie_button = self._driver.find_element(By.XPATH, cookie_agree_xpath)
            if WebDriverWait(self._driver, 5).until(ec.element_to_be_clickable(cookie_button)):
                cookie_button.click()
                self.logger.debug(F"Parser pass cookie modal on page: {self._driver.current_url}")
        except NoSuchElementException as e:
            self.logger.debug(f'modal agree not found on page: {self._driver.current_url}')

    def find_document(self, _doc: SPP_document):
        """
        Метод для обработки найденного документа источника
        """
        if self._last_document and self._last_document.hash == _doc.hash:
            raise Exception(f"Find already existing document ({self._last_document})")

        if self._max_count_documents and len(self._content_document) >= self._max_count_documents:
            raise Exception(f"Max count articles reached ({self._max_count_documents})")

        self._content_document.append(_doc)
        self.logger.info(self._find_document_text_for_logger(_doc))

