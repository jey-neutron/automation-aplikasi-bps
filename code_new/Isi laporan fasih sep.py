import time
import tempfile
import os
import logging
from pathlib import Path

# Library
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import pandas as pd
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


# config
logger = logging.getLogger(__name__)
this_path = Path().resolve()
#fd, path = tempfile.mkstemp(prefix="temp",dir=this_path)

# func
def writetemp_input(text):
    #with os.fdopen(fd, 'w') as tmp:
    with open('temp_input.txt','w') as tmp:
        tmp.write(text)
def cek_input(namafile='temp_input.txt'):
    if Path(str(this_path)+f"/{namafile}").exists():
        return True # berarti ada suruh nginput

# for main view func
def desc():
    # desc memuat keterangan program, sso buat apa, nama survei di fasih, dataframe used, rentang baris
    return "1) Program untuk ngisi laporan SEP di Fasih-sm \n 2) SSO untuk login Fasih \n 3) Nama survei isiin SURVEI PELAPORAN LAPANGAN SEP 2024 \n 4) CSV gunakan assign_cawi, tapi harus diedit tiap saat yah sebelum run program dan nama sheetnya samain nama file \n 5) Rentang baris menandakan kode kec. Amannya satu2 karna Fasihnya perlu kode antirobot"

def RUN(ssoname, ssopass, pilihan_survei, df_name, rentang):
    try:
        # Open mozilla
        logger.info("# Opening mozilla ")
        # add profile extension automa
        profile = webdriver.FirefoxProfile() 
        if Path("../automa-1.28.27.xpi").is_file():
            logger.info("with added extension")
            profile.add_extension(extension='../automa-1.28.27.xpi')
        driver = webdriver.Firefox(executable_path = "../geckodriver.exe", firefox_profile=profile)

        # GET TO URL
        logger.info("# Opening fasih-sm.bps.go.id, udah login vpn?")
        #input('# Jika udah, PRESS ENTER')
        driver.get('https://fasih-sm.bps.go.id')

        # Login SSO
        WebDriverWait(driver, 15).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
        ).click()
        # input SSO
        WebDriverWait(driver, 15).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
        driver.find_element_by_xpath('//*[@id="username"]').send_keys(ssoname)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(ssopass)
        driver.find_element_by_xpath('//*[@id="kc-login"]').send_keys(Keys.RETURN)

        # wait until muncul pilihan survei
        time.sleep(10)
        WebDriverWait(driver, 15).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.CSS_SELECTOR, "h4.card-title")) #finding the element
        )
        for i in range(1, int(driver.find_element_by_xpath('id("Pencacahan_info")').text.split(' ')[3] )):
            namasurveiweb = driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').text
            if namasurveiweb == pilihan_survei:
                break
        driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').click()
        time.sleep(3)

        from win10toast import ToastNotifier
        ## notification for windows os
        class MyToastNotifier(ToastNotifier):
            def __init__(self):
                super().__init__()
            def on_destroy(self, hwnd, msg, wparam, lparam):
                super().on_destroy(hwnd, msg, wparam, lparam)
                return 0
        notif = MyToastNotifier()
        #notif.show_toast("Assign fasih PY", "YEYYY SELESE :)", duration = 1)

        # read df
        logger.info("WARN: Cek dulu df nya")
        df = pd.read_excel(str(this_path)+"/"+df_name, sheet_name=df_name.split(".")[0])
        logger.info(df.head())
        
        # ALL run
        ikec = rentang
        if "-" in str(ikec):
            ikec0 = int ( str(ikec).split[0] )
            ikec1 = int ( str(ikec).split[1] )
        else :
            ikec0 = int(ikec)
            ikec1 = ikec0+1
        for ikec in range(ikec0,ikec1):
        #for ikec in range(2,7):
            # filter df per ikec duls
            dff = df[df.kec == ikec].reset_index()
            logger.info("# Banyaknya data: "+ str(len(dff)))
            # click link bersangkutan kec
            for row in range(0, 6):
                #linkkec = driver.find_element_by_css_selector(f'.ng-star-inserted:nth-child({row+1}) > td:nth-child(2) > a')
                linkkec = driver.find_element_by_xpath(f'id("assignmentDatatable")/TBODY[2]/TR[{row+1}]/TD[2]/A[1]')
                if linkkec.text == f"51030{ikec}0":
                    logger.info(f"# Found n goto link: href/{linkkec.text}")
                    # goto link
                    #linkkec.click()
                    driver.get(str(linkkec.get_attribute("href")))
                    break
                #else:
                #    raise Exception('BREAK, GANEMU')
            # click btn review
            time.sleep(3)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-primary")) ).click()
            ## wait till loading nya ilang
            logger.info(f"# Loading form")
            time.sleep(5)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(3)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

            # EDIT. link click
            logger.info('# Click edit')
            driver.find_element_by_css_selector('a.btn-primary').click()
            ## wait till loading nya ilang
            time.sleep(1)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(1)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

            logger.info("# Ngisi data... ")
            for row in range(0, len(dff)):
                #alt 1
                #idbsweb = driver.find_element_by_xpath()
                #alt 2
                my_element_xpath = f'id("nested_nbs___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]/DIV[1]/TABLE[1]/TBODY[1]/TR[{row+1}]/TD[1]/DIV[1]'
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                WebDriverWait(driver, timeout=50, ignored_exceptions=ignored_exceptions)\
                                        .until(expected_conditions.presence_of_element_located((By.XPATH, my_element_xpath)))
                idbsweb = driver.find_element_by_xpath(my_element_xpath)

                #if idbsweb.text == dff.idbs[row]:
                #print(idbsweb.text, dff.idbs[row],idbsweb.text == dff.idbs[row])
                logger.info(f"{row+1} {idbsweb.text} {idbsweb.text == dff.idbs[row]}")
                if idbsweb.text != dff.idbs[row]:
                    pesan = '# MAAF ROW "WEB FASIH" MA "DF" GA SAMA, BREAK DULU'
                    logger.warning("WARN: "+pesan)
                    notif.show_toast("Auto fasih PY", pesan, duration = 1)
                    raise Exception(pesan)

                #do ngisi
                time.sleep(1)
                # kondisi
                time.sleep(0.5)
                driver.find_element_by_css_selector(f'input#inputMaskkondisi\#{row+1}').clear()
                time.sleep(0.2)
                driver.find_element_by_css_selector(f'input#inputMaskkondisi\#{row+1}').send_keys(" "+dff.date[row])
                driver.find_element_by_css_selector(f'input#inputMaskkondisi\#{row+1}').send_keys(Keys.TAB)
                # status
                time.sleep(0.5)
                driver.find_element_by_css_selector(f'#status\#{row+1}___container .formgear-input-papi').clear()
                time.sleep(0.2)
                driver.find_element_by_css_selector(f'#status\#{row+1}___container .formgear-input-papi').send_keys(str(dff.status[row]))
                # utp selese
                time.sleep(0.5)
                driver.find_element_by_css_selector(f'#selesai_utp\#{row+1}___container .formgear-input-papi').clear()
                time.sleep(0.2)
                driver.find_element_by_css_selector(f'#selesai_utp\#{row+1}___container .formgear-input-papi').send_keys(str(dff.utp_selesai[row]))


                #else:
                #    print('KOK GA SAMA')
                #    continue

            # submit
            time.sleep(1)
            driver.find_element_by_css_selector('button.bg-teal-300').click()
            logger.warning("WARN: Attention, open terminal and firefox. Abistu balikin ke SURVEY COLLECTION trus open SURVEI PELAPORAN SEP")
            pesan = "SUDAH SELEEE" if ikec != 6 else "I NEED UR ATTENTION"
            notif.show_toast("Auto fasih PY", pesan, duration = 1)
            input(f"{datetime.datetime.now()} | PAUSED, Input anything to continue")
        logger.info('SELESEEEEE')
        print(f"{datetime.datetime.now()} | Dah kembali ke browser")
        driver.close()

        # log
        #writetemp_input('input yah')
        #logger.info('WARN')
        # menunggu dihapus
        #while cek_input():
        #    time.sleep(1)
        time.sleep(2)
        return("Program selesai di jalankan")
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.error('WARN: Error happen')
        notif.show_toast("Auto fasih PY", "Error happen", duration = 1)
        return (f"Error: {str(e)}, type error: {exc_type}, on file: {fname} on line {exc_tb.tb_lineno}")