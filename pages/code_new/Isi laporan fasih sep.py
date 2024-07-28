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
import _EDIT
logger = logging.getLogger(__name__)
this_path = Path().resolve()
#fd, path = tempfile.mkstemp(prefix="temp",dir=this_path)
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
# looprentang
def getlistloop(rentang):
    if "-" in str(rentang):
        ikec0 = int ( str(rentang).split('-')[0] )
        ikec1 = int ( str(rentang).split('-')[1] )+1
        looprentang = range(ikec0,ikec1)
    elif "," in str(rentang):
        looprentang = str(rentang).split(',')
        looprentang = [int(i) for i in looprentang]
    elif int(rentang):
        looprentang = range(int(rentang), int(rentang)+1)
    return (looprentang)

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
    return """1) Program untuk ngisi laporan SEP di Fasih-sm 
2) SSO untuk login Fasih 
3) Nama survei isiin `SURVEI PELAPORAN LAPANGAN SEP 2024`
4) Gsheet masukkan sheetID dan sheetname, tapi harus diedit tiap saat yah sebelum run program <br> Kolom df: `'kec'` adalah kode kec dalam integer, `'date'` adalah date now dengan format `'dd mm yyyy'`, `'status'` kode status dalam integer, `'utp_selesai'` jml utp selesai dalam integer
5) Rentang baris menandakan `kode kec`. Amannya satu2 karna Fasihnya perlu kode antirobot, tapi bisa multikec pakai koma atau rentang"""

def RUN(ssoname, ssopass, tab_survei, pilihan_survei, df_name,sheet_name, rentang, hide_ff, close_ff = True):
    try:
        # cek df dulu
        df = ''
        columns_wajib = ['kec','date','status','utp_selesai']
        logger.info(f'Data yang mau dipake adalah {df_name}. Kolom wajib ada: {columns_wajib} ')
        # read df yang terpilih
        logger.info("Checking df")
        #df = pd.read_excel(str(this_path)+"/"+df_name, sheet_name=df_name.split(".")[0])
        url = f"https://docs.google.com/spreadsheets/d/{df_name}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        try:
            df = pd.read_csv(url, on_bad_lines='skip')
        except:
            df = ''
        columns_df = [x for x in columns_wajib if x in df.columns]
        logger.info(f"DF= Data head :\n{df.head()}")
        ## cek kolom data csv
        if columns_df != columns_wajib: 
            kataerror = '# Maaf data tidak memenuhi kriteria. \nKolom wajib ada: '+str(columns_wajib)+\
            '\nData anda: '+str([i for i in df.columns])+\
            '\nSilakan cek data kembali'
            logger.info("WARN: "+kataerror)
            notif.show_toast("Auto fasih PY", "ERROR HAPPEN :(", duration = 1)
            raise Exception(kataerror)
            #exit
        logger.info("Df valid")
        
        # Open mozilla
        logger.info("Opening mozilla ")
        driver = _EDIT.open_ff(headless=hide_ff)
        
        # GET TO URL
        logger.info("Opening fasih-sm.bps.go.id, udah login vpn?")
        #input('# Jika udah, PRESS ENTER')
        try:
            driver.get('https://fasih-sm.bps.go.id')
        except Exception as e: raise Exception ('Gabisa buka, maintenance ato blm make vpn ga? '+str(e))

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
        def xpath_exist(xpath):
            try:
                driver.find_element_by_xpath(xpath)
                return True
            except:    
                return False

        # click pelatihan
        if tab_survei == 1:
            idtableinfo = "Pencacahan_info"
            idtable = "Pencacahan"
        if tab_survei == 2:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ng-star-inserted:nth-child(2) > .nav-link'))
            ).click()
            idtableinfo = "DataTables_Table_2_info" if xpath_exist(f'id("DataTables_Table_2_info")') else "DataTables_Table_0_info"
            idtable = "DataTables_Table_2" if xpath_exist(f'id("DataTables_Table_2_info")') else "DataTables_Table_0"
        if tab_survei == 3:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ng-star-inserted:nth-child(3) > .nav-link'))
            ).click()
            idtableinfo = "DataTables_Table_5_info" if xpath_exist(f'id("DataTables_Table_5_info")') else "DataTables_Table_1_info"
            idtable = "DataTables_Table_5" if xpath_exist(f'id("DataTables_Table_5_info")') else "DataTables_Table_1"
        # 
        time.sleep(6)
        pilihan_survei = pilihan_survei.strip()
        print("Searching the survey from ("+driver.find_element_by_xpath(f'id("{idtableinfo}")').text+")")
        jmlsurvei = int(driver.find_element_by_xpath(f'id("{idtableinfo}")').text.split(' ')[3] )
        for i in range(1, jmlsurvei+1):
            namasurveiweb = driver.find_element_by_xpath(f'id("{idtable}")/TBODY[1]/TR[{i}]/TD[1]/A[1]').text
            if namasurveiweb == pilihan_survei:
                print(f"Found nama survey: {namasurveiweb} == {pilihan_survei}, opening link")
                break
            elif i==jmlsurvei and namasurveiweb != pilihan_survei: 
                print('Survey not found')
                raise Exception('Survey not found')
        driver.find_element_by_xpath(f'id("{idtable}")/TBODY[1]/TR[{i}]/TD[1]/A[1]').click()
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

        #zoom
        driver.execute_script("document.body.style.MozTransform='scale(0.7)';")
        driver.execute_script("document.body.style.MozTransformOrigin='0 0';")

        # ALL run
        looprentang = getlistloop(rentang)
        for ikec in looprentang:
        #for ikec in range(2,7):
            # filter df per ikec duls
            dff = df[df.kec == ikec].reset_index()
            logger.info("Banyaknya data: "+ str(len(dff)))
            # click link bersangkutan kec
            for row in range(0, 6):
                #linkkec = driver.find_element_by_css_selector(f'.ng-star-inserted:nth-child({row+1}) > td:nth-child(2) > a')
                WebDriverWait(driver,60).until( #using explicit wait for x seconds
                    EC.presence_of_element_located((By.XPATH, f'id("assignmentDatatable")/TBODY[2]/TR[{row+1}]/TD[2]/A[1]')) #finding the element
                )
                linkkec = driver.find_element_by_xpath(f'id("assignmentDatatable")/TBODY[2]/TR[{row+1}]/TD[2]/A[1]')
                if linkkec.text == f"51030{ikec}0":
                    logger.info(f"Found n goto link: href/{linkkec.text}")
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
            logger.info(f"Loading form")
            time.sleep(5)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(3)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

            # EDIT. link click
            #zoom
            driver.execute_script("document.body.style.MozTransform='scale(0.7)';")
            driver.execute_script("document.body.style.MozTransformOrigin='0 0';")
            logger.info('Click edit')
            try:
                WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'a.btn-primary')))
            except:
                pass
            # scroll top
            driver.execute_script("return arguments[0].scrollIntoView(true);", driver.find_element_by_css_selector('a.btn-primary'))
            driver.find_element_by_css_selector('a.btn-primary').click()
            ## wait till loading nya ilang
            time.sleep(1)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(1)
            WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

            #zoom
            driver.execute_script("document.body.style.MozTransform='scale(0.7)';")
            driver.execute_script("document.body.style.MozTransformOrigin='0 0';")
            logger.info("Ngisi data... ")
            for row in range(0, len(dff)):
                #alt 1
                #idbsweb = driver.find_element_by_xpath()
                #alt 2
                #my_element_xpath = f'id("nested_nbs___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]/DIV[1]/TABLE[1]/TBODY[1]/TR[{row+1}]/TD[1]/DIV[1]'
                #ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                #WebDriverWait(driver, timeout=60, ignored_exceptions=ignored_exceptions)\
                #                        .until(expected_conditions.presence_of_element_located((By.XPATH, my_element_xpath)))
                #idbsweb = driver.find_element_by_xpath(my_element_xpath)
                #alt 3
                #action_chain = ActionChains(driver)     
                #action_chain.double_click(driver.find_element_by_xpath("//tr[2]/p")).perform()
                #idbsweb = action_chain(driver.find_element_by_xpath(my_element_xpath))
                try:
                    idbsweb = driver.find_element_by_css_selector(f'#kdwil_nbs\#{row+1}___container .formgear-input-papi').get_attribute('value')
                except:
                    idbsweb = 'error getting data'
                    pass

                #if idbsweb.text == dff.idbs[row]:
                #print(idbsweb.text, dff.idbs[row],idbsweb.text == dff.idbs[row])
                #logger.info(f"{row+1} {idbsweb.text} {idbsweb.text == dff.idbs[row]} {dff.idbs[row]}")
                logger.info(f"{row+1}/{str(len(dff))} {idbsweb} {dff.idbs[row]}")
                # if idbsweb.text != dff.idbs[row]:
                #     pesan = 'MAAF ROW "WEB FASIH" MA "DF" GA SAMA, BREAK DULU'
                #     logger.warning("WARN: "+pesan)
                #     notif.show_toast("Auto fasih PY", pesan, duration = 1)
                #     raise Exception(pesan)

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
            pesan = "OPEN FIREFOX"
            if ikec == looprentang[-1]:
                pesan = "SUDAH SELEEE"
                break
            notif.show_toast("Auto fasih PY", pesan, duration = 1)
            confirm = input(f"{datetime.datetime.now()} | PAUSED, ending of '0{ikec}0', Press 'enter' to continue")
            if confirm:
                print(f"{datetime.datetime.now()} | Dah kembali ke browser, terminal di minimize aja yah")
            print(f"{datetime.datetime.now()} | Dah kembali ke browser, terminal di minimize aja yah")
            time.sleep(20)
            logger.info('Continuing next iteration')
        logger.info('SELESEEEEE')
        driver.close()

        # log
        #writetemp_input('input yah')
        #logger.info('WARN')
        # menunggu dihapus
        #while cek_input():
        #    time.sleep(1)
        time.sleep(2)
        return("Program selesai di jalankan. NOTE!!!!! Kalo download result, bakalan langsung ke page home", df)
    
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