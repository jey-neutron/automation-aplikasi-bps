import logging
import os
import sys
import time
import pandas as pd
from pathlib import Path

# Library
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# to stale
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
import csv
import sys

#config
logger = logging.getLogger(__name__)
this_path = Path().resolve()
from win10toast import ToastNotifier
# notification for windows os
class MyToastNotifier(ToastNotifier):
    def __init__(self):
        super().__init__()
    def on_destroy(self, hwnd, msg, wparam, lparam):
        super().on_destroy(hwnd, msg, wparam, lparam)
        return 0
notif = MyToastNotifier()
#notif.show_toast("Assign fasih PY", "YEYYY SELESE :)", duration = 1)

# for main view func
def desc():
    # desc memuat keterangan program, sso buat apa, nama survei di fasih, dataframe used, rentang baris
    return """1) Program untuk mendapatkan data sampel dari row Fasih-sm 
2) SSO untuk login fasih 
3) Nama survei isiin survei yang mau diambil datanya, samain dengan nama di Fasih ya 
4) Dataframe gsheet ga digunakan, isi terserah gapapa
5) Rentang baris isi `0` aja jika get sampel semuanya dari awal (menandakan row keberapa di Fasih) <br> *[Sementara format yang bisa adalah `a` atau `a-c`. Jika masukin format `a,b,c` maka akan error]*"""

def RUN(ssoname, ssopass, pilihan_survei, df_name,sheet_name, rentang, close_ff=True):
    try:
        df = ''
        # Open mozilla
        logger.info("Opening mozilla ")
        # add option mozilla
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--width=1000")
        opts.add_argument("--height=800")
        # add profile extension automa
        profile = webdriver.FirefoxProfile() 
        if Path("../automa-1.28.27.xpi").is_file():
            logger.info("with added extension")
            profile.add_extension(extension='../automa-1.28.27.xpi')
        driver = webdriver.Firefox(executable_path = str(this_path)+"/"+"geckodriver.exe", firefox_profile=profile, options=opts)

        # GET TO URL
        logger.info("Opening fasih-sm.bps.go.id, udah login vpn?")
        #input('# Jika udah, PRESS ENTER')
        driver.get('https://fasih-sm.bps.go.id')

        # Login SSO
        WebDriverWait(driver, 15).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
        ).click()
        # input SSO
        logger.info("Loading, dont do anything")
        WebDriverWait(driver, 15).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
        driver.find_element_by_xpath('//*[@id="username"]').send_keys(ssoname)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(ssopass)
        driver.find_element_by_xpath('//*[@id="kc-login"]').send_keys(Keys.RETURN)

        # wait until muncul pilihan survei
        time.sleep(6)
        WebDriverWait(driver,60).until( #using explicit wait for x seconds
            #EC.presence_of_element_located((By.CSS_SELECTOR, "h4.card-title")) #finding the element
            #EC.presence_of_element_located((By.CSS_SELECTOR, "div#Pencacahan_info")) #finding the element
            EC.presence_of_element_located((By.XPATH, 'id("Pencacahan_info")')) #finding the element
        )
        time.sleep(6)
        logger.info("Searching the survey from ("+driver.find_element_by_xpath('id("Pencacahan_info")').text+")")
        jmlsurvei = int(driver.find_element_by_xpath('id("Pencacahan_info")').text.split(' ')[3] )
        for i in range(1, jmlsurvei+1):
            namasurveiweb = driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').text
            if namasurveiweb == pilihan_survei:
                break
            elif i==jmlsurvei and namasurveiweb!=pilihan_survei: 
                raise Exception('Survey not found')
        logger.info(f"Found nama survey: {namasurveiweb} == {pilihan_survei}, opening link")
        driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').click()
        time.sleep(3)

        # cek if pilih survei sudah oke
        periode_survei = Select(driver.find_element_by_css_selector('select.custom-select')).first_selected_option
        notif.show_toast("Assign fasih PY", "Cek periode survei", duration = 1)
        logger.info(f"WARN: Cek dulu periode survei = {periode_survei.text} ? 5detik, Abaikan jika udah dicek") #.getattributevalue
        time.sleep(5)
        # show 100 row
        selectshow=Select(driver.find_element_by_xpath('id("assignmentDatatable_length")/LABEL[1]/SELECT[1]'))
        selectshow.select_by_index(3)
        time.sleep(2)

        # RUN ALL
        # get jml kolom in sampel fasih
        jmlhead = driver.find_elements_by_xpath('id("assignmentDatatable")/THEAD[1]/TR[1]/TD')
        logger.info(f"Getting data with {len(jmlhead)} columns")
        isirow = []
        for col in range(1,len(jmlhead)+1):
            isirow.append(driver.find_element_by_xpath(f'id("assignmentDatatable")/THEAD[1]/TR[1]/TD[{str(col)}]').text)
        # with open(f'log {pilihan_survei}_sampel.csv','w',newline='') as fd:
        #     writer = csv.writer(fd)
        #     writer.writerow([0]+isirow)
        columns = isirow
        df = pd.DataFrame([], columns=columns)
        #row_max = int(driver.find_element_by_css_selector('div#assignmentDatatable_info').text.split()[5]) # get num of all rows
        #numrow = 0 # initiate from row start (default value = 0)
        numpage = 1 # page number

        if "-" in str(rentang):
            numrow = int ( str(rentang).split[0] )
            row_max = int ( str(rentang).split[1] )+1
        else :
            numrow = int(rentang)
            row_max = int(driver.find_element_by_css_selector('div#assignmentDatatable_info').text.split()[5]) # get num of all rows

        # get isi
        logger.info(f"Getting from rows {numrow} until {row_max}")
        while numrow < row_max:
            #print("\npage: "+str(numpage))
            #print(" row progress:", end='')
            # get jml row
            jml_row = len(driver.find_elements_by_xpath('id("assignmentDatatable")/TBODY[2]/TR')) #len row in that page
            # loop per row in this page
            for row in range(1,jml_row+1):
                numrow += 1 # get this row
                isirow = []
                for col in range(1,len(jmlhead)+1):
                    isirow.append(driver.find_element_by_xpath(f'id("assignmentDatatable")/TBODY[2]/TR[{str(row)}]/TD[{str(col)}]').text)
                # write 1 row to csv
                #logger.info(isirow)
                # with open(f'log {pilihan_survei}_sampel.csv','a',newline='') as fd:
                #     writer = csv.writer(fd)
                #     writer.writerow([numrow]+isirow)
                df = df._append(pd.DataFrame([isirow], columns=columns), ignore_index=True)
                #print(row, col, isirow)
                #print(numrow, end=" ")
                logger.info(f"Getting data onrow= {numrow}, onpage= {numpage}")
            
            #next page
            numpage+=1
            time.sleep(0.5)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, 'id("assignmentDatatable_next")')) ).click()
            
        time.sleep(2)
        logger.info('SELESEEEEE')
        driver.close()
        return("Program selesai di jalankan, hasil file bisa didownload. NOTE!!!!! Kalo download result, bakalan langsung ke page home", df)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.error('WARN: Error happen')
        notif.show_toast("Auto fasih PY", "Error happen", duration = 1)
        if close_ff:
            try:
                driver.close()
            except:
                pass
        return (f"Error: {str(e)}, type error: {exc_type}, on file: {fname} on line {exc_tb.tb_lineno}. NOTE!!!!! Bisa download result, tapi bakalan langsung ke page home", df)