def RUN():
    ## Try all
    try:
        print("# First time opening bakalan install library, kalo udah nginstall, close and run ulang aj\nKlo ERROR run ulang :'")
        ## Loop try importing Library
        while True:
            ## if have thes lib
            try:
                from getpass import getpass
                from selenium import webdriver
                #from selenium.webdriver.firefox.service import Service
                from selenium.webdriver.common.keys import Keys
                from selenium.webdriver.common.action_chains import ActionChains
                import time
                import datetime
                import pandas as pd
                from selenium.webdriver.support.ui import Select
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.common.by import By
                from selenium.webdriver.common.action_chains import ActionChains
                #import IPython
                import csv
                from win10toast import ToastNotifier
                #from IPython.display import Audio
                #sound_file = '../sound.mp3'
                break
            ## If dont have that lib, then install them
            except:
                import sys
                import subprocess
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', "win10toast==0.9", 'PyYAML==3.11'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', "selenium==3.141.0", 'PyYAML==3.11'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', "urllib3==1.26.16", 'PyYAML==3.11'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', "pandas", 'PyYAML==3.11'])
        ## end true importing library
        import os
        os.system('cls')
        

        ## notification for windows os
        class MyToastNotifier(ToastNotifier):
            def __init__(self):
                super().__init__()
            def on_destroy(self, hwnd, msg, wparam, lparam):
                super().on_destroy(hwnd, msg, wparam, lparam)
                return 0
        notif = MyToastNotifier()
        
        ## Intro info login SSO    
        print('# GET DATA FASIH-SM v12.04.2024 #\n[untuk request lain hubungi admin dulu de] \n')
        print('# Masukin SSO untuk login fasih (password emang gamuncul, \nketik aja trus enter kalo udah):')
        #ssoname = input("Username SSO: ")
        #ssopass = getpass("Password SSO: ")
        from _EDIT import sso_pegawai as user
        ssoname = user['username']
        ssopass = user['password']
        
        ## Open mozilla
        print("# Opening mozilla, tunggu buka dulu")
        #s = Service(r'../geckodriver.exe')
        driver = webdriver.Firefox(executable_path = "geckodriver.exe")
        #        service_log_path="C:\\Users\\[username]\\AppData\\Local\\Temp\\geckodriver.log")
        
        try:
            ## GET TO URL
            print("# Opening fasih-sm.bps.go.id")
            #notif.show_toast("Get fasih PY", "I Need U to PRESS ENTER :(", duration = 1)
            #input("# Udah make vpn? Jika udah, PRESS ENTER")
            driver.get('https://fasih-sm.bps.go.id')
            print("# Loading, don't do anything")

            ## Login SSO
            WebDriverWait(driver, 60).until( #using explicit wait for x seconds
                EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
            ).click()
            ## input SSO
            WebDriverWait(driver, 60).until( #using explicit wait for x seconds
                EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
            driver.find_element_by_xpath('//*[@id="username"]').send_keys(ssoname)
            driver.find_element_by_xpath('//*[@id="password"]').send_keys(ssopass)
            driver.find_element_by_xpath('//*[@id="kc-login"]').send_keys(Keys.RETURN)
        except:
            raise Exception("Login SSO dulu")

        ## !! Pilih survei
        WebDriverWait(driver, 100).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, 'id("navbarUserDropdown")/SPAN[1]/IMG[1]')) )
        notif.show_toast("Get fasih PY", "I Need U to MILIH SURVEY :(", duration = 1)
        input('# Pilih survei yang mau diassign \n(sampe milih bulan kalau emang survei bulanan DAN completed_by_pengawas jika perlu).\nJika udah, PRESS ENTER')
        ##

        ## Gettin data FASIH-SM
        dfrow = 1
        gagal = 0
        ## jika gagal blm tw
        time.sleep(1)
        #notif.show_toast("Get fasih PY", "I Need U to PRESS ENTER :(", duration = 1)
        #input("# PRESS ENTER to Start Gettin")
        
        print('# Start gettin data fasih --- ')
        print()
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
                    print(f"{now}| {dfrow}| {nm_usaha[:20]}")
                    ## klik link di kode identitas
                    driver.find_elements_by_css_selector('.ng-star-inserted:nth-child('+str(dfrow)+') > td:nth-child(2) > a')[0].click()
                    print("# Opening n loading... ")
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

                    print("# Getting data... ")
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
                        #print(blok1[7])
                    except Exception as e:
                        dfrow += 1
                        with open('Get_fasih_sm_SKTNPlog.csv','a',newline='') as fd:
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
                            #print(dvw, blok30)
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
                    print("# DONE")
                    ## write csv
                    with open('Get_fasih_sm_log.csv','a',newline='') as fd:
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
                    print('# Error terjadi: '+str(e))
                    time.sleep(3)
                    ## !! BLM TAW HANDLINGNYA
                    with open('Get_fasih_sm_log.csv','a',newline='') as fd:
                        writer = csv.writer(fd)
                        writer.writerow([now]+[i]+["","",nm_usaha, "GAGAL: "+str(e)])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    gagal += 1
                    if gagal >= 50:
                        print("# Udah gagal 50X, dah males ah")
                        break
                    continue
                            
            
                #start = dfrow-1
                #if start <0: start = 0
                #gagal += 1
                #print('# Gagal:',gagal)
                ## lemme ngitung diff time each attempt yang gagal. 
                ## 7annya cuman pengen kalo 5x attempt gagal waktunya cuman < 3s maka BREAK, biar ga lama2 sampe 100 baru break
                #listgagal = []
                #listgagal.append(now)
                #if len(listgagal)>5:
                #    listgagal.pop(0) #remove timegagal index pertama
                #    diff = listgagal[4]-listgagal[0] #itung delta time
                #    difftime = divmod(diff.days * seconds_in_day + diff.seconds, 1)[0]

                #if gagal%2 == 0 :
                #    driver.refresh()
                #    time.sleep(5)
                    ########
                    ## !! Komen di bawah ini perlu jika tiap refresh bulan surveinya berbeda. or apalah ketentuannya
                    ########
                    #notif.show_toast("Get fasih PY", "I Need U to MILIH SURVEY lagi :(", duration = 1)
                #    print('# Refreshing')
                #    print("# Restart lagi at row: ",start)
                #    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                #        EC.presence_of_element_located((By.CSS_SELECTOR, 'td.sorting_disabled:nth-child(2)')) )
                #    continue
                #if ((gagal >100) OR (difftime<3)): #!! jika different time gagalnya gagal maka remove aja OR blabla nya
                    #Audio(sound_file, autoplay=True)
                #    print("# Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))
                #    notif.show_toast("Get fasih PY", "ERROR HAPPEN :(", duration = 1)
                #    raise Exception("# Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))
                #    break
                #print("# Restart lagi at row: ",start)
                #continue
                
            
        ## play notif
        #Audio(sound_file, autoplay=True)
        print('SLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEESE')
        notif.show_toast("Get fasih PY", "YEYYY SELESE :)", duration = 1)
        input("CLOSE PROGRAMS")
       
    ## except all
    except Exception as e:
        print("\n# Error: "+str(e))
        notif.show_toast("Get fasih PY", "ERROR HAPPEN :(", duration = 1)
        input("CLOSE AND RESTART")
