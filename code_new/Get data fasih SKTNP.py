import logging
import os
import sys
import time
import pandas as pd
from pathlib import Path

# Library
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import csv
import sys
import datetime

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

# for main view func
def desc():
    # desc memuat keterangan program, sso buat apa, nama survei di fasih, dataframe used, rentang baris
    return """1) Program untuk mendapatkan data dari isian fasih 
2) SSO untuk login Fasih 
3) Nama survei isiin `SKTNP 2024` (sesuaiin Fasih) <br> <span class='note'> NOTE!!!!! </span> Lapus kode `10` dan `17` blm pernah ada, jadi mungkin data yang lapusnya itu, data terambilnya beda
4) Dataframe gsheet ga digunakan, isi terserah gapapa
5) Rentang baris isi `1` aja jika get sampel semuanya dari awal (menandakan row keberapa di Fasih) <br> *[Sementara blm berguna sih, baru ditampilin `1-jml row ditampilin` aja]*
"""

def RUN(ssoname, ssopass, pilihan_survei, df_name,sheet_name, rentang, close_ff=True):
    try:
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
        logger.info(f"Searching the survey from ({driver.find_element_by_xpath('id("Pencacahan_info")').text})")
        jmlsurvei = int(driver.find_element_by_xpath('id("Pencacahan_info")').text.split(' ')[3] )
        for i in range(1, jmlsurvei):
            namasurveiweb = driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').text
            if namasurveiweb == pilihan_survei:
                break
            elif i==jmlsurvei: 
                raise Exception('Survey not found')
        logger.info(f"Found nama survey: {namasurveiweb} == {pilihan_survei}, opening link")
        driver.find_element_by_xpath(f'id("Pencacahan")/TBODY[1]/TR[{i}]/TD[1]/A[1]').click()
        time.sleep(3)

        # cek if pilih survei sudah oke
        periode_survei = Select(driver.find_element_by_css_selector('select.custom-select')).first_selected_option
        notif.show_toast("Assign fasih PY", "Cek periode survei", duration = 1)
        logger.info(f"WARN: Cek dulu periode survei = {periode_survei.text} ? Abaikan jika udah dicek") #.getattributevalue
        time.sleep(5)
        # show 100 row
        selectshow=Select(driver.find_element_by_xpath('id("assignmentDatatable_length")/LABEL[1]/SELECT[1]'))
        selectshow.select_by_index(3)
        time.sleep(2)

        # RUN ALL
        ## Gettin data FASIH-SM
        dfrow = 1
        gagal = 0
        ## jika gagal blm tw
        time.sleep(1)
        #notif.show_toast("Get fasih PY", "I Need U to PRESS ENTER :(", duration = 1)
        #input("# PRESS ENTER to Start Gettin")
        
        logger.info('Start gettin data fasih --- ')
        ## switch to origin tab
        driver.switch_to.window(driver.window_handles[0])
        ## Jumlah row yang ditampilin di fasih
        #jml_row = 10+1
        jml_row = int(driver.find_element_by_css_selector('div#assignmentDatatable_info').text.split()[3]) + 1
        for i in range(1,jml_row): ## loop row fasih
            while True:
                try:
                    now = datetime.datetime.now()
                    ## print nama usaha
                    nm_usaha = driver.find_elements_by_css_selector('.ng-star-inserted:nth-child('+str(dfrow)+') > .ng-star-inserted:nth-child(3)')[0].text
                    logger.info(f"{dfrow}| {nm_usaha[:20]}")
                    ## klik link di kode identitas
                    driver.find_elements_by_css_selector('.ng-star-inserted:nth-child('+str(dfrow)+') > td:nth-child(2) > a')[0].click()
                    logger.info("Opening n loading... ")
                    ## switch to new tab
                    driver.switch_to.window(driver.window_handles[1])
                    ## click btn review
                    time.sleep(3)
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-primary")) ).click()
                    ## wait till loading nya ilang
                    time.sleep(5)
                    WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
                    ## wait till rendering form
                    time.sleep(3)
                    WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

                    # init log file
                    if not Path(f'{this_path}/log {pilihan_survei}_sampel.csv').exists():
                        with open(f'log {pilihan_survei}_sampel.csv','w',newline='') as fd:
                            writer = csv.writer(fd)
                            writer.writerow(['timestamp', 'row', 'kec', 'desa', 'r105', 'r106', 'r17', 'r108', 'r109', 'r110', 'kbli', 'blok21satuan', 'blok21a', 'blok21b', 'blok21c', 'blok21d', 'blok21e', 'blok21f', 'blok22satuan', 'blok22a', 'blok22b', 'blok22c', 'blok22d', 'blok22e', 'blok22f', 'blok30satuan', 'blok30a', 'blok30b', 'blok30c', 'blok30d', 'blok30e', 'blok30f', 'blok31satuan', 'blok31a', 'blok31b', 'blok31c', 'blok31d', 'blok32e', 'blok32f', 'blok33satuan', 'blok33a', 'blok33b', 'blok33c', 'blok33d', 'blok33e', 'blok33f', 'blok34satuan', 'blok34a', 'blok34b', 'blok34c', 'blok34d', 'blok34e', 'blok34f', 'r401', 'r402a', 'r402b', 'r402c', 'r402d', 'r402e', 'r402f', 'r403', 'r403value', 'r404', 'r405', 'catatan'])

                    logger.info("Getting data... ")
                    blok1 = ["","","","","","","","",""]
                    blok21 = ["","","","","","",""]
                    blok22 = ["","","","","","",""]
                    blok3 = []
                    blok4 = ["","","","","","","","","","",""]
                    blok5 = ''
                    ## get blok I
                    blok1[0] = driver.find_element_by_xpath('id("kec___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]').text
                    blok1[1] = driver.find_element_by_xpath('id("desa___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]').text
                    blok1[2] = driver.find_element_by_xpath('id("b1r105___container")/DIV[1]/DIV[2]/DIV[1]/INPUT[1]').get_attribute('value')
                    blok1[3] = driver.find_element_by_xpath('id("b1r106___container")/DIV[1]/DIV[2]/DIV[1]/INPUT[1]').get_attribute('value')
                    blok1[4] = driver.find_element_by_xpath('id("b1r107___container")/DIV[1]/DIV[2]/DIV[1]/INPUT[1]').get_attribute('value')
                    blok1[5] = driver.find_element_by_xpath('id("b1r108___container")/DIV[1]/DIV[2]/DIV[1]/INPUT[1]').get_attribute('value')
                    try:
                        blok1[6] = driver.find_element_by_xpath('id("b1r109___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]').text
                        if blok1[6] == "": raise Exception("r109 blank")
                        blok1[7] = driver.find_element_by_xpath('id("b1r110___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]').text
                        blok1[8] = driver.find_element_by_xpath('id("kbli___container")/DIV[1]/DIV[2]/DIV[1]/DIV[1]').text
                        #logger.info(blok1[7])
                    except Exception as e:
                        dfrow += 1
                        #with open('Get_fasih_sm_SKTNPlog.csv','a',newline='') as fd:
                        with open(f'log {pilihan_survei}_sampel.csv','a',newline='') as fd:
                            writer = csv.writer(fd)
                            writer.writerow([now]+[i]+blok1+["",nm_usaha, "Data ga lengkap: "+str(e)])
                        break
                        #raise Exception("Sorry, data ga lengkap "+str(e))
                    time.sleep(1)
                    
                    ## click blok II
                    driver.find_elements_by_css_selector('.formgear-sidebar:nth-child(2) > li > .block')[0].click()
                    ## click view 1
                    driver.find_elements_by_css_selector('button#nestedButton-roster_blok2-0')[0].click()
                    blok21[0] = driver.find_element_by_xpath('id("b2_k2#1___container")/DIV[1]/DIV[2]/INPUT[1]').get_attribute('value')
                    blok21[1] = driver.find_element_by_xpath('id("numberInput4")').get_attribute('value')
                    blok21[2] = driver.find_element_by_xpath('id("numberInput6")').get_attribute('value')
                    blok21[3] = driver.find_element_by_xpath('id("numberInput8")').get_attribute('value')
                    blok21[4] = driver.find_element_by_xpath('id("numberInput11")').get_attribute('value')
                    blok21[5] = driver.find_element_by_xpath('id("numberInput13")').get_attribute('value')
                    blok21[6] = driver.find_element_by_xpath('id("numberInput15")').get_attribute('value')
                    ## click next btn to view 2
                    driver.find_elements_by_css_selector('button.h-10:nth-child(3)')[0].click()
                    blok22[0] = driver.find_element_by_xpath('id("b2_k2#2___container")/DIV[1]/DIV[2]/INPUT[1]').get_attribute('value')
                    blok22[1] = driver.find_element_by_xpath('id("numberInput4")').get_attribute('value')
                    blok22[2] = driver.find_element_by_xpath('id("numberInput6")').get_attribute('value')
                    blok22[3] = driver.find_element_by_xpath('id("numberInput8")').get_attribute('value')
                    blok22[4] = driver.find_element_by_xpath('id("numberInput11")').get_attribute('value')
                    blok22[5] = driver.find_element_by_xpath('id("numberInput13")').get_attribute('value')
                    blok22[6] = driver.find_element_by_xpath('id("numberInput15")').get_attribute('value')

                    ## click next btn to blok 3 
                    driver.find_elements_by_css_selector('button.h-10:nth-child(3)')[0].click()
                    # view in blok 3 for 4x
                    for dvw in range(0,4):
                        blok30 = [0,0,0,0,0,0,0]
                        kd = ['3','4','5','7','8','9']
                        try: 
                            time.sleep(1)
                            ## rincian beda per lapus
                            if blok1[7].split()[0]=="1" : kde="01"; kd[0]="3"; kd[1]="4"; kd[2]='5'; kd[3]='7'; kd[4]='8'; kd[5]='9'
                            elif blok1[7].split()[0]=="2" or blok1[7].split()[0]=='3': kde="02"; kd[0]="3"; kd[1]="4"; kd[2]='5'; kd[3]='7'; kd[4]='8'; kd[5]='9'
                            elif blok1[7].split()[0]=="4" : kde="03"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10'
                            elif blok1[7].split()[0]=="5" : kde="04"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10'
                            elif blok1[7].split()[0]=="6" : kde="05"; kd[0]="3"; kd[1]="4"; kd[2]='5'; kd[3]='7'; kd[4]='8'; kd[5]='9'
                            elif blok1[7].split()[0]=="7" : kde="06"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10'
                            elif blok1[7].split()[0]=="8" or blok1[7].split()[0]=='9': kde="07"; kd[0]="3"; kd[1]="4"; kd[2]='5'; kd[3]='7'; kd[4]='8'; kd[5]='9'
                            elif blok1[7].split()[0]=="10" : kde="08"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10' ##blm ada
                            elif blok1[7].split()[0]=="11" : kde="09"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10'
                            elif blok1[7].split()[0]=="12" or blok1[7].split()[0]=='13' or blok1[7].split()[0]=='14' or blok1[7].split()[0]=='15' : 
                                kde="10"; kd[0]="3"; kd[1]="4"; kd[2]='5'; kd[3]='7'; kd[4]='8'; kd[5]='9'
                            elif blok1[7].split()[0]=="16" : kde="11"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10'
                            elif blok1[7].split()[0]=="17" : kde="12"; kd[0]="4"; kd[1]="5"; kd[2]='6'; kd[3]='8'; kd[4]='9'; kd[5]='10' ##blm ada
                            ## click view    
                            driver.find_elements_by_css_selector('button#nestedButton-roster_r3'+kde+'-'+str(dvw))[0].click()
                            blok30[0] = driver.find_element_by_xpath('id("b3r3'+kde+'_k2#'+str(dvw+1)+'___container")/DIV[1]/DIV[2]/INPUT[1]').get_attribute('value')
                            blok30[1] = driver.find_element_by_xpath('id("numberInput'+kd[0]+'")').get_attribute('value')
                            blok30[2] = driver.find_element_by_xpath('id("numberInput'+kd[1]+'")').get_attribute('value')
                            blok30[3] = driver.find_element_by_xpath('id("numberInput'+kd[2]+'")').get_attribute('value')
                            blok30[4] = driver.find_element_by_xpath('id("numberInput'+kd[3]+'")').get_attribute('value')
                            blok30[5] = driver.find_element_by_xpath('id("numberInput'+kd[4]+'")').get_attribute('value')
                            blok30[6] = driver.find_element_by_xpath('id("numberInput'+kd[5]+'")').get_attribute('value')
                            #logger.info(dvw, blok30)
                            blok3.append(blok30)
                            ## click blok3 awal
                            driver.find_elements_by_css_selector('.formgear-sidebar:nth-child(3) > li > .block')[0].click()
                        except:
                            blok3.append(blok30)
                            continue

                    ## click blok 4
                    driver.find_elements_by_css_selector('.formgear-sidebar:nth-child(1) .block')[0].click()
                    time.sleep(1)
                    driver.find_elements_by_css_selector('.formgear-sidebar:nth-child(4) .block')[0].click()
                    try:
                        blok4[0] = driver.find_element_by_xpath('id("b4r401_k2___container")/DIV[1]/DIV[2]/INPUT[1]').get_attribute('value')
                        blok4[1] = driver.find_element_by_xpath('id("numberInput4")').get_attribute('value')
                        blok4[2] = driver.find_element_by_xpath('id("numberInput6")').get_attribute('value')
                        blok4[3] = driver.find_element_by_xpath('id("numberInput8")').get_attribute('value')
                        blok4[4] = driver.find_element_by_xpath('id("numberInput11")').get_attribute('value')
                        blok4[5] = driver.find_element_by_xpath('id("numberInput13")').get_attribute('value')
                        blok4[6] = driver.find_element_by_xpath('id("numberInput15")').get_attribute('value')
                        for dvw in range(0,3):
                            if (driver.find_element_by_xpath('id("radio-b4r403-'+str(dvw)+'")').is_selected()):
                                blok4[7] = dvw+1
                                break
                        blok4[8] = driver.find_element_by_xpath('id("decimalInput20")').get_attribute('value')
                        blok4[9] = driver.find_element_by_xpath('id("growth___container")/DIV[1]/DIV[2]/INPUT[1]').get_attribute('value')
                        blok4[10] = driver.find_element_by_xpath('id("b4r405___container")/DIV[1]/DIV[2]/DIV[1]/TEXTAREA[1]').get_attribute('value')
                    except:
                        pass

                    ## click next btn to blok 5
                    driver.find_elements_by_css_selector('button.h-10:nth-child(3)')[0].click()
                    blok5 = [driver.find_element_by_xpath('id("b5___container")/DIV[1]/DIV[2]/DIV[1]/TEXTAREA[1]').get_attribute('value').strip()]

                    ## click back btn
                    #driver.find_elements_by_css_selector('.space-x-10 > .bg-blue-700:nth-child(1)')[0].click()
                    logger.info("DONE")
                    ## write csv
                    with open(f'log {pilihan_survei}_sampel.csv','a',newline='') as fd:
                        writer = csv.writer(fd)
                        writer.writerow([now]+[i]+blok1+blok21+blok22+blok3[0]+blok3[1]+blok3[2]+blok3[3]+blok4+[blok5])
                    ## close tab n back to tab origin
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    dfrow += 1
                    break #while true (sukses)
                    
                    ###################
                    ## !! HANDLING JIKA UDAH SELESE 1 PAGE INI
                    ## vv ada data yg nol RICEK
                    ## vv loop row ga berubah sampe >10 jika error
                    ###################

                ## jika gagal print error
                except Exception as e:
                    logger.info('Error terjadi: '+str(e))
                    time.sleep(3)
                    ## !! BLM TAW HANDLINGNYA
                    with open(f'log {pilihan_survei}_sampel.csv','a',newline='') as fd:
                        writer = csv.writer(fd)
                        writer.writerow([now]+[i]+["","",nm_usaha, "GAGAL: "+str(e)])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    gagal += 1
                    if gagal >= 50:
                        logger.info("Udah gagal 50X, dah males ah")
                        break
                    continue
            
        time.sleep(2)
        logger.info('SELESEEEEE')
        driver.close()
        return("Program selesai di jalankan, hasil file ada di ➡️ "+f'log {pilihan_survei}_sampel.csv')
    
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
        return (f"Error: {str(e)}, type error: {exc_type}, on file: {fname} on line {exc_tb.tb_lineno}")
