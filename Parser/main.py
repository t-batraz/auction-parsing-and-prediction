import time
from AuctionParser import Parser


src = input('src')
login = input('login')
password = input('password')
parser = Parser(src=src)
parser.preprocessing(login=login, password=password)
parser.start_parsing()