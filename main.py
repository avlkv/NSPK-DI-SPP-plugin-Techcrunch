from selenium import webdriver

from logging import config

config.fileConfig('dev.logger.conf')
from Techcrunch import Techcrunch

driver = webdriver.Chrome()

parser = Techcrunch(driver)
docs = parser.content()

print(*docs, sep='\n\r\n')
