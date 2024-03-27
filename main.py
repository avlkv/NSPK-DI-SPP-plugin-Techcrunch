from selenium import webdriver

from logging import config
from src.spp.types import SPP_document
config.fileConfig('dev.logger.conf')
from Techcrunch import Techcrunch
import pickle
import pandas
# driver = webdriver.Chrome()
#
# parser = Techcrunch(driver)
# docs = parser.content()
#
# print(*docs, sep='\n\r\n')
config.fileConfig('dev.logger.conf')


def driver():
    """
    Selenium web driver
    """
    options = webdriver.ChromeOptions()

    # Параметр для того, чтобы браузер не открывался.
    # options.add_argument('headless')

    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    return webdriver.Chrome(options)


def to_dict(doc: SPP_document) -> dict:
    return {
        'title': doc.title,
        'abstract': doc.abstract,
        'text': doc.text,
        'web_link': doc.web_link,
        'local_link': doc.local_link,
        'other_data': '',
        'pub_date': str(doc.pub_date.timestamp()) if doc.pub_date else '',
        'load_date': str(doc.load_date.timestamp()) if doc.load_date else '',
    }


parser = Techcrunch(driver())
docs: list[SPP_document] = parser.content()
print(*docs, sep='\n\r\n')

try:
    with open('documents.backup.pkl', 'wb') as file:
        pickle.dump(docs, file)
except Exception as e:
    print(e)

try:
    dataframe = pandas.DataFrame.from_records([to_dict(d) for d in docs])
    dataframe.to_csv('techcrunch_documents_20231229.csv', index = False)
except Exception as e:
    print(e)

print(*docs, sep='\n\r\n')