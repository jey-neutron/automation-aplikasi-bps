import logging
import os
import sys
import time
import pandas as pd
from pathlib import Path

# Libr
from selenium import webdriver
#from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
import time
import datetime
import pandas as pd
import numpy as np
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from argparse import Action
#import IPython
import csv
from win10toast import ToastNotifier
#from IPython.display import Audio
#sound_file = '../sound.mp3'

#config
logger = logging.getLogger(__name__)
this_path = Path().resolve()
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
def getlistloop(rentang):
    if "," in str(rentang):
        kolom = str(rentang).split(',')
        kolom = [int(i) for i in kolom]
    else:
        raise Exception('Dibilang suruh isi nomor kolom yang sesuai kok ya :(')
    return (kolom)

# for main view func
def desc():
    # desc memuat keterangan program, sso buat apa, nama survei di fasih, dataframe used, rentang baris
    return "1) Program untuk auto assign by selection di Fasih berdasarkan csv \n 2) SSO untuk login Fasih \n 3) Nama survei isiin survei yang mau diassign, samain dengan nama di Fasih ya \n 4) CSV gunakan assign_daftar, tapi harus diedit tiap saat yah sebelum run program \n Kolom df: 'nm_sampel', 'alamat', 'email_petugas', 'usersso_pengawas' \n NOTE!!!!! Untuk 'usersso_pengawas' kalo pengawasnya organik, isiin tanpa '@bps.go.id' yah \n 5) NOTE!!!!! Rentang kolom isi 'x,y,z' \n Nomor kolom x = kolom nama sampel \n Nomor kolom y = kolom alamat \n Nomor kolom z = kolom user saat ini \n Liat di Fasih berarti, kolom centang paling kiri adalah nomor kolom 1"

def RUN(ssoname, ssopass, pilihan_survei, df_name, rentang, close_ff=True):
    try:
        # cek df dulu
        columns_wajib = ['nm_sampel','alamat','email_petugas','usersso_pengawas']
        logger.info(f'Data yang mau dipake adalah {df_name}. Kolom wajib ada: {columns_wajib} ')
        # read df yang terpilih
        logger.info("Checking df")
        df = pd.read_csv(str(this_path)+"/"+df_name)
        columns_df = [x for x in columns_wajib if x in df.columns]
        logger.info(f"DF= Data head :\n{df.head()}")
        ## cek kolom data csv
        if columns_df != columns_wajib: 
            kataerror = '# Maaf data tidak memenuhi kriteria. \nKolom wajib ada: '+str(columns_wajib)+\
            '\nData anda: '+str([i for i in df.columns])+\
            '\nSilakan cek data kembali'
            logger.info("WARN: "+kataerror)
            notif.show_toast("Assign fasih PY", "ERROR HAPPEN :(", duration = 1)
            raise Exception(kataerror)
            #exit
        logger.info("Df valid")
        df['result_log'] = np.nan

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
        time.sleep(6)
        logger.info(f"Searching the survey from ({driver.find_element_by_xpath('id("Pencacahan_info")').text})")
        for i in range(1, int(driver.find_element_by_xpath('id("Pencacahan_info")').text.split(' ')[3] )):
            namasurveiweb = driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').text
            if namasurveiweb == pilihan_survei:
                break
        logger.info("Found nama survey, opening link")
        driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').click()
        time.sleep(3)

        # cek if pilih survei sudah oke
        periode_survei = Select(driver.find_element_by_css_selector('select.custom-select')).first_selected_option
        notif.show_toast("Assign fasih PY", "Cek periode survei", duration = 1)
        logger.info(f"WARN: Cek dulu periode survei = {periode_survei.text} ? Abaikan jika udah dicek") #.getattributevalue
        time.sleep(5)
        #input(f"{datetime.datetime.now()} | Pilih survei yang mau diassign \n(sampe milih bulan kalau emang survei bulanan).\nJika udah, PRESS ENTER")
        #print(f"{datetime.datetime.now()} | Dah kembali ke browser)

        ## !! Pilih kolom yang diperlukan untuk searching dan matching
        #nama x, alamat y, usersaatini z
        kolomnama, kolomalamat, kolomuser = getlistloop(rentang)

        ## Assign
        start = 0 #perlu dicustom lagi si
        end = len(df)
        gagal = 0
        rowgada = 0
        count_gagal_sebelum_nyerah = 50 #perlu dicustom lagi si
        ## jika gagal loop terus :""
        time.sleep(1)
        #notif.show_toast("Assign fasih PY", "I Need U to PRESS ENTER :(", duration = 1)
        #input("# PRESS ENTER to Start Assigning")
        
        logger.info('\n Start assigning fasih --- ')
        while True:
            ## loop per row daftar_assign csv
            try:
                for dfrow in range(start,end): ## loop row df
                    ## Search by namalamat
                    now = datetime.datetime.now()
                    logger.info(f"{df.index[dfrow]}| {df.nm_sampel[dfrow]}")
                    searchbar = driver.find_element_by_xpath('id("assignmentDatatable_filter")/LABEL[1]/INPUT[1]')
                    searchbar.clear()
                    searchbar.send_keys(df.nm_sampel[dfrow], Keys.RETURN)
                    time.sleep(2)

                    ## match (nama DAFTAR SAMPEL.csv HARUS SAMA DENGAN DAFTAR SAMPEL FASIH)
                    try: 
                        ## cek ada isian row ato tidak
                        WebDriverWait(driver, 5).until( #using explicit wait for x seconds
                          EC.presence_of_element_located((By.XPATH, 'id("assignmentDatatable")/TBODY[2]/TR[1]/TD[3]')) )
                        pass
                    except: 
                        ## jika kosong maka CONT
                        logger.info(f'{df.index[dfrow]}|↪️ kosong')
                        #with open('log Assign_fasih.csv','a', newline='') as fd:
                        #    writer = csv.writer(fd)
                        #    writer.writerow([df.index[dfrow], now, df.alamat[dfrow], df.nm_sampel[dfrow], "tidak ada di fasih"])
                        df.loc[df.index[dfrow], 'result_log'] = 'kosong'
                        continue
                        
                    ## Jumlah row yang ditampilin di fasih
                    #jml_row = 10+1
                    jml_row = int(driver.find_element_by_css_selector('div#assignmentDatatable_info').text.split()[3]) + 1
                    
                    for i in range(1,jml_row): ## loop row fasih, cek row yang diinginkan
                        ## cek nama kolom
                        headusersaatini = driver.find_elements_by_css_selector(f'.thead-bps td:nth-child({str(kolomuser)})')[0].text
                        #if headusersaatini!="User Saat ini": raise Exception("Kolom sudah berubah, hubungi admin suruh sesuaikan lagiii")
                        
                        id_web = driver.find_elements_by_css_selector(f'.ng-star-inserted:nth-child({str(i)}) > .ng-star-inserted:nth-child({str(kolomnama)})')[0].text + \
                            driver.find_elements_by_css_selector(f'.ng-star-inserted:nth-child({str(i)}) > .ng-star-inserted:nth-child({str(kolomalamat)})')[0].text
                        usersaatini = driver.find_elements_by_css_selector(f'.ng-star-inserted:nth-child({str(i)}) > td:nth-child({str(kolomuser)})')[0].text
                        #driver.find_element_by_xpath('id("assignmentDatatable")/TBODY[2]/TR['+i+']/TD[5]').text()

                        ## cek kesamaan
                        if (df.nm_sampel[dfrow]+df.alamat[dfrow] == id_web):
                            #print('== ')
                            rowgada = 0 #lanjut karna dah nemu yang sama
                            break #break loop row fasih
                        else:
                            rowgada = 1 #akan next loop
                            break
                    ## jika gada row yang sama maka CONT next loop,
                    if (rowgada == 1):
                        logger.info(f'{df.index[dfrow]}|↪️ ganemu, mungkin kosong')
                        #with open('log Assign_fasih.csv','a', newline='') as fd:
                        #    writer = csv.writer(fd)
                        #    writer.writerow([df.index[dfrow], now, df.alamat[dfrow], df.nm_sampel[dfrow], "ganemu, mungkin tidak ada di fasih, ricek"])
                        df.loc[df.index[dfrow], 'result_log'] = 'ganemu, mungkin kosong'
                        continue
                    ## cek row matching and tick jika user saat ini masi ()
                    tick = 0
                    if (usersaatini !='()'): 
                        ## jika dah ke assign maka CONT
                        logger.info(f'{df.index[dfrow]}|↪️ skip dah ke assign ke '+usersaatini)
                        ## write log
                        #with open('log Assign_fasih.csv','a', newline='') as fd:
                        #    writer = csv.writer(fd)
                        #    writer.writerow([df.index[dfrow], now,df.alamat[dfrow], df.nm_sampel[dfrow], usersaatini, df.email_petugas[dfrow]])
                        df.loc[df.index[dfrow], 'result_log'] = 'skip dah ke assign ke '+usersaatini
                        continue #next loop row df
                    else:
                        tick = 1
                        ## tick centang buat select by assign
                        driver.find_elements_by_css_selector('.ng-star-inserted:nth-child('+str(i)+') > td > .ng-untouched')[0].click()
                        #.ng-star-inserted:nth-child(2) > td > .ng-untouched

                    ## dropdown assign
                    driver.find_elements_by_css_selector('.btn-group:nth-child(3) > .dropdown-toggle')[0].click() #dropdown assign button
                    driver.find_elements_by_css_selector('.show > .dropdown-item:nth-child(1)')[0].click() #pilihan assign by selection
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, "//BODY/NGB-MODAL-WINDOW[1]/DIV[1]/DIV[1]/APP-MODAL-ASSIGN[1]/DIV[2]/DIV[1]/DIV[1]/NGX-SELECT[1]/DIV[1]/DIV[2]/DIV[1]")) #finding the element
                    )
                    ## assign pengawas
                    driver.find_elements_by_css_selector('.form-group:nth-child(1) > .col-md-6 .ngx-select__toggle')[0].click()
                    driver.find_elements_by_css_selector('input.ngx-select__search')[0].send_keys(df.usersso_pengawas[dfrow])
                    time.sleep(1.2)
                    driver.find_elements_by_css_selector('a.ngx-select__item')[0].click()
                    time.sleep(1)
                    ## assign petugas
                    driver.find_elements_by_css_selector('.form-group:nth-child(2) > .col-md-6 .ngx-select__toggle')[0].click()
                    driver.find_elements_by_css_selector('input.ngx-select__search')[0].send_keys(df.email_petugas[dfrow])
                    time.sleep(1)
                    driver.find_elements_by_css_selector('a.ngx-select__item')[0].click()
                    ## konfirm ok assign 
                    #driver.find_elements_by_css_selector('button.btn-primary:nth-child(1)')[0].send_keys(Keys.RETURN) 
                    ## klik assign btn
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary:nth-child(1)")) #assign btn
                    ).click()
                    ## klik konfirmasi 
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        #EC.presence_of_element_located((By.XPATH, "//BODY/DIV[2]/DIV[1]/DIV[6]/BUTTON[1]")) #konfirmasi
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm")) #konfirmasi
                    ).click()
                    
                    ## jika gamau ilang modalnya setelah konfirm
                    try:
                        WebDriverWait(driver, 2).until( #using explicit wait for x seconds
                            #EC.presence_of_element_located((By.XPATH, "//BODY/DIV[2]/DIV[1]/BUTTON[1]"))
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button.swal2-close")) #close berhasil tapi error jika ada
                        ).click()
                        #time.sleep(1)
                        ## close modal selection petugas
                        driver.find_elements_by_css_selector('button.close')[0].click()
                        status_msg = WebDriverWait(driver,2).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "ngb-modal-window.modal")))
                        Action.move_to_element(status_msg).perform()
                        status_msg.find_element_by_css_selector("button.close").click()
                    except: pass
                    
                    if (tick == 1): #then untick
                        driver.find_elements_by_css_selector('.ng-star-inserted:nth-child('+str(i)+') > td > .ng-untouched')[0].click()
                        tick = 0
                    logger.info(f'{df.index[dfrow]}|↪️ sukses assign ke '+df.email_petugas[dfrow])
                    ## write log
                    #with open('log Assign_fasih.csv','a', newline='') as fd:
                    #    writer = csv.writer(fd)
                    #    writer.writerow([df.index[dfrow], now,df.alamat[dfrow], df.nm_sampel[dfrow], usersaatini, df.email_petugas[dfrow]])
                    df.loc[df.index[dfrow], 'result_log'] = 'sukses assign ke '+df.email_petugas[dfrow]

                logger.info('SLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEESE')
                notif.show_toast("Assign fasih PY", "YEYYY SELESE :)", duration = 1)
                break
                            
            ## jika gagal print error
            except Exception as e:
                logger.info('Error terjadi: '+str(e))
                start = dfrow-1
                if start <0: start = 0
                gagal += 1
                logger.info('Gagal:',gagal)
                ## lemme ngitung diff time each attempt yang gagal. 
                ## 7annya cuman pengen kalo 5x attempt gagal waktunya cuman < 3s maka BREAK, biar ga lama2 sampe 100 baru break
                listgagal = []
                listgagal.append(now)
                difftime = 4
                if len(listgagal)>5:
                    listgagal.pop(0) #remove timegagal index pertama
                    diff = listgagal[4]-listgagal[0] #itung delta time
                    #difftime = divmod(diff.days * seconds_in_day + diff.seconds, 1)[0]
                    difftime = diff.seconds

                if gagal%2 == 0 :
                    logger.info('Refreshing')
                    driver.refresh()
                    time.sleep(5)
                    ########
                    ## !! Komen di bawah ini perlu jika tiap refresh bulan surveinya berbeda. or apalah ketentuannya
                    ########
                    #notif.show_toast("Assign fasih PY", "I Need U to MILIH SURVEY lagi :(", duration = 1)
                    logger.info("Periode Survei benar?: ", driver.find_element_by_css_selector("select.custom-select").get_attribute("value") )
                    time.sleep(5)
                    logger.info("Restart lagi at row: ",start)
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'td.sorting_disabled:nth-child(2)')) )
                    continue
                if ((gagal > count_gagal_sebelum_nyerah) or (difftime<3)): #!! jika different time gagalnya gagal maka remove aja OR blabla nya
                    #Audio(sound_file, autoplay=True)
                    logger.info("WARN: Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))
                    notif.show_toast("Assign fasih PY", "ERROR HAPPEN :(", duration = 1)
                    raise Exception("Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))
                    
                logger.info("Restart lagi at row: ",start)
                continue
            
        # end run
        driver.close()
        df.to_csv(str(this_path)+"/log "+df_name)
        logger.info('Log result hasil dapat diliat di '+str(this_path)+"/log "+df_name)
        return("Program selesai di jalankan")
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.error('WARN: Error happen')
        notif.show_toast("Auto fasih PY", "Error happen", duration = 1)
        try:
            df.to_csv(str(this_path)+"/log "+df_name)
            logger.info('Log result hasil dapat diliat di '+str(this_path)+"/log "+df_name)
            if close_ff:
                driver.close()
        except:
            pass
        return (f"Error: {str(e)}, type error: {exc_type}, on file: {fname} on line {exc_tb.tb_lineno}")
