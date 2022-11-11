import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient


class Parser():
    def __init__(self, src):
        self.src = src
        self.driver = webdriver.Chrome(src)
        self.driver.get(self.src)

        self.client = MongoClient('localhost', 27017)
        self.db = self.client['japain_auction_cars']
        self.lot_collection = self.db['auction_cars']

    def wait_response(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'aj_view0')))
        time.sleep(0.5)

    def logining(self, login, password):
        btn_vhod = self.driver.find_element(by=By.ID, value="aj_login_but_r")
        btn_vhod.click()

        login_field = self.driver.find_element(by=By.XPATH,
                                               value="// input[ @ name = 'username']")
        login_field.send_keys(login)

        password_field = self.driver.find_element(by=By.XPATH,
                                                  value="//input[@id='auth_passwd']")
        password_field.send_keys(password)

        btn_vhod = self.driver.find_element(by=By.XPATH,
                                            value="//input[@value='вход']")
        btn_vhod.click()
        time.sleep(1)

        self.driver.get(self.src)
        time.sleep(1)

    def select_car_type(self):
        b_toyota = self.driver.find_element(by=By.XPATH, value="//a[@id='aj1_1']")
        b_toyota.click()

        search_btn = self.driver.find_element(by=By.XPATH,
                                              value="//a[@class='search_button_export aj_offf']")
        search_btn.click()
        self.wait_response()

    def set_min_year(self, year=2000):
        year_field_activate = self.driver.find_element(by=By.XPATH,
                                                       value="//tbody/tr/td[@id='aj_out_SL']/div[1]/div[1]/a[1]")
        year_field_activate.click()
        self.wait_response()

        year_set = self.driver.find_element(by=By.XPATH,
                                            value="//input[@id='yearN']")
        for i in range(4):
            year_set.send_keys(Keys.BACKSPACE)
        year_set.send_keys(str(year))

    def selec_only_saled_cars(self):
        saled_set = self.driver.find_element(by=By.XPATH,
                                             value="//nobr[contains(text(),'продан')]")
        saled_set.click()

        search_btn = self.driver.find_element(by=By.XPATH,
                                              value="//a[@class='search_button_export aj_offf']")
        search_btn.click()
        self.wait_response()

    def set_50_cars_in_page(self):
        list_size_50 = self.driver.find_element(by=By.XPATH,
                                                value="//a[@id='list_size_50']")
        list_size_50.click()
        self.wait_response()

    def order_by_date(self):
        order_by_auc_date = self.driver.find_element(by=By.XPATH, value=
        "/html[1]/body[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/table[1]/tbody[1]/tr[2]/td[1]/div[3]/div[1]/div[1]/table[2]/tbody[1]/tr[1]/td[3]/table[1]/tbody[1]/tr[1]/td[1]/a[1]"
                                                     )
        order_by_auc_date.click()
        self.wait_response()

    def preprocessing(self, login, password):
        preprocessing_start_time = time.time()
        self.logining(login=login, password=password)
        self.select_car_type()
        self.set_min_year()
        self.selec_only_saled_cars()
        self.set_50_cars_in_page()
        self.order_by_date()
        preprocessing_finish_time = time.time()
        print(f'Preprocessing time {preprocessing_finish_time - preprocessing_start_time} s')

    def get_lot_scr_number(self, row):
        try:
            td1 = row.find_element(by=By.CLASS_NAME, value='my_bids')
            try:
                src = td1.get_attribute('href')
            except:
                src = '_'
            try:
                lot_number = str(td1.text).rstrip().lstrip()
            except:
                lot_number = -99999
        except:
            src, lot_number = '_', -99999
        return src, lot_number

    def get_date_acution(self, row):
        try:
            date = row.find_element(by=By.CLASS_NAME, value='ffix_time').text[:10]
            date = date.rstrip().lstrip()
        except:
            date = '01.01.1980'
        try:
            auction = row.find_element(by=By.CSS_SELECTOR,
                                       value='[style="word-break:break-all"]').text
            auction = auction.rstrip().lstrip()
        except:
            auction = '_'
        return date, auction

    def get_model_year_body_options(self, row):
        try:
            td3 = row.find_element(by=By.CSS_SELECTOR, value='[style = "width:100px;line-height:1.2em"]')
            try:
                model = td3.find_element(by=By.CSS_SELECTOR,
                                         value='[style="font-size:11px;font-family:Tahoma;color:#6db3eb;line-height:1em"]').text
                model = model.rstrip().lstrip()
            except:
                model = '_'
            try:
                year = td3.find_element(by=By.CSS_SELECTOR, value='[style="color:#a93f15"]').text[:4]
                year = year.rstrip().lstrip()
            except:
                year = '01.01.1980'
            try:
                body_model = td3.find_element(by=By.CSS_SELECTOR, value='[style="color:#a93f15"]').text[5:]
                body_model = body_model.rstrip().lstrip()
            except:
                body_model = '_'
            try:
                options_packag = td3.find_element(by=By.CLASS_NAME, value="grade_hide").text
                options_packag = options_packag.rstrip().lstrip()
            except:
                options_packag = '_'
        except:
            model, year, body_model, options_packag = '_', '01.01.1980', '_', '_'
        return model, year, body_model, options_packag

    def get_trans_engine_cond_colr_drive_power(self, row):
        try:
            td4 = row.find_element(by=By.CSS_SELECTOR,
                                   value='[style = "max-width:90px"]')
            try:
                div = td4.find_element(by=By.CSS_SELECTOR,
                                       value='[style="line-height:1.2em"]')
                try:
                    transmission = div.find_element(by=By.CSS_SELECTOR,
                                                    value='[style="color:#a93f15"]').text
                except:
                    transmission = '_'
                try:
                    cond_type = div.find_element(by=By.CSS_SELECTOR,
                                                 value='[class="aj_equip"]').text
                except:
                    cond_type = '_'
            except:
                transmission, cond_type = '_', '_'
            try:
                engine = td4.find_element(by=By.CSS_SELECTOR,
                                          value='[style="line-height:1.2em"]').text
                engine = max([int(i) for i in engine.split() if i.isdigit()])
            except:
                engine = -99999
            try:
                color = td4.find_element(by=By.CSS_SELECTOR,
                                         value='[style="color:#aaa;font-size:10px"]').text
            except:
                color = '_'
            try:
                power = td4.find_element(by=By.CSS_SELECTOR,
                                         value='[style = "font-family:Tahoma;color:#aaa;font-size:10px"]').text
                power = np.mean([int(i) for i in power.split(',')])
            except:
                power = -99999
            try:
                drive = td4.find_elements(by=By.CSS_SELECTOR,
                                          value='[style="color:#aaa;font-size:10px"]')[1].text
            except:
                drive = '_'
        except:
            transmission, engine, cond_type, color, power, drive = '_', -99999, '_', '_', -99999, '_'
        return transmission, engine, cond_type, color, power, drive

    def get_condition_odometer(self, row):
        try:
            odometer = row.find_element(by=By.CSS_SELECTOR,
                                        value='[style="display:inline-block;font-size:12px;background:"]').text
            odometer = int(odometer.split()[0])
        except:
            odometer = 0
        try:
            condition = row.find_element(by=By.CSS_SELECTOR,
                                         value='[style="color:#73aa00;font-family:Arial;font-size:13px"]').text
        except:
            condition = '_'
        return condition, odometer

    def get_star_sale_price(self, row):
        try:
            td5 = row.find_element(by=By.CLASS_NAME, value='ffix_price')
            try:
                start_price = td5.find_element(by=By.CLASS_NAME,
                                               value='aj_price_start').text[:-1].replace(' ', '')
            except:
                start_price = 0
            try:
                sale_price = td5.find_element(by=By.CLASS_NAME,
                                              value='ajCurr_sold').text[:-1].replace(' ', '')
            except:
                sale_price = -99999
        except:
            start_price, sale_price = -99999, -99999
        return start_price, sale_price

    def table_parser(self, table):
        for elem_num in range(50):
            row = table.find_element(by=By.ID, value=f'aj_view{elem_num}')

            scr, lot_number = self.get_lot_scr_number(row)
            date, auction = self.get_date_acution(row)
            model, year, body_model, options_packag = self.get_model_year_body_options(row)
            transmission_type, engine_displacement, air_conditioner_type, \
            color, power, drive_type = self.get_trans_engine_cond_colr_drive_power(row)
            condition, odometer = self.get_condition_odometer(row)
            start_price, sale_price = self.get_star_sale_price(row)

            lot_info = {
                'scr': scr,
                'lot_number': lot_number,
                'auction_date': date,
                'auction_place': auction,
                'car_model': model,
                'car_year': year,
                'body_model': body_model,
                'transmission_type': transmission_type,
                'engine_displacement': engine_displacement,
                'air_conditioner_type': air_conditioner_type,
                'car_color': color,
                'horse_power': power,
                'drive_type': drive_type,
                'auction_condition_rating': condition,
                'odometer': odometer,
                'auction_start_price': start_price,
                'sale_price': sale_price
            }
            try:
                self.lot_collection.insert_one(lot_info)
            except:
                print('lot not added')

    def start_parsing(self, start=1, finish=1000):
        parsing_start_time = time.time()
        for page_number in range(start, finish + 1):
            if page_number != 1:
                select_page = self.driver.find_element(by=By.CSS_SELECTOR,
                                                       value=f'[onclick="navi(this,{page_number});"]')
                select_page.click()
                self.wait_response()

            table = self.driver.find_element(by=By.XPATH,
                                             value="//table[@class='t_main']")
            self.table_parser(table)
            if page_number % 1 == 0:
                t = time.time() - parsing_start_time
                h = round(t // 60 // 60)
                min = round(t // 60 % 60)
                sec = round(t % 60)
                print(f'page_number:{page_number}, time:{h}.{min}.{sec}')
