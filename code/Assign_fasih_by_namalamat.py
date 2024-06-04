from argparse import Action


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
        print('# ASSIGN FASIH VIA NAMA ALAMAT SAMPEL v12.05.2024 #\n[untuk yang gada nama & alamat hubungi admin dulu de] \n')
        print('# Masukin SSO untuk login fasih (password emang gamuncul, \nketik aja trus enter kalo udah):')
        from _EDIT import sso_pegawai as user
        ssoname = user['username']
        ssopass = user['password']
        
        print('# Data yang mau diassign ada di `assign_daftar.csv`. Kolom wajib ada:')
        columns_wajib = ['nm_sampel','alamat','email_petugas','usersso_pengawas']
        print(columns_wajib)

        ## Read data csv yang mo diassign
        print('# Reading assign_daftar.csv')
        df = pd.read_csv('assign_daftar.csv')
        df.index += 1
        print("Size row data: ", len(df))
        print("Columns: ", [i for i in df.columns])
        df.usersso_pengawas = df.usersso_pengawas.str.split('@').str[0]
        print(df)
        
        columns_df = [x for x in columns_wajib if x in df.columns]
        ## cek kolom data csv
        if columns_df != columns_wajib: 
            kataerror = '# Maaf data tidak memenuhi kriteria. \nKolom wajib ada: '+str(columns_wajib)+\
            '\nData anda: '+str([i for i in df.columns])+\
            '\nSilakan cek data kembali'
            print(kataerror)
            notif.show_toast("Assign fasih PY", "ERROR HAPPEN :(", duration = 1)
            raise Exception(kataerror)
            #exit
        
        ## Open mozilla
        print("# Opening mozilla, tunggu buka dulu")
        #s = Service(r'../geckodriver.exe')
        driver = webdriver.Firefox(executable_path = "geckodriver.exe")
        #        service_log_path="C:\\Users\\[username]\\AppData\\Local\\Temp\\geckodriver.log")
        
        try:
            ## GET TO URL
            print("# Opening fasih-sm.bps.go.id")
            #notif.show_toast("Assign fasih PY", "I Need U to PRESS ENTER :(", duration = 1)
            #input("# Udah make vpn? Jika udah, PRESS ENTER")
            driver.get('https://fasih-sm.bps.go.id')
            print("# Loading, don't do anything")

            ## Login SSO
            WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
            ).click()
            ## input SSO
            WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
            driver.find_element_by_xpath('//*[@id="username"]').send_keys(ssoname)
            driver.find_element_by_xpath('//*[@id="password"]').send_keys(ssopass)
            driver.find_element_by_xpath('//*[@id="kc-login"]').send_keys(Keys.RETURN)
        except:
            raise Exception("Login SSO dulu")

        ## !! Pilih survei
        WebDriverWait(driver, 100).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, 'id("navbarUserDropdown")/SPAN[1]/IMG[1]')) )
        notif.show_toast("Assign fasih PY", "I Need U to MILIH SURVEY :(", duration = 1)
        input('# Pilih survei yang mau diassign \n(sampe milih bulan kalau emang survei bulanan).\nJika udah, PRESS ENTER')
        ## !! Pilih kolom yang diperlukan untuk searching dan matching
        print('\n# Isi isian berikut: (kolom centang paling kiri adalah nomor kolom 1)')
        colnousersaatini = input('Input nomor kolom untuk "User Saat Ini":')
        colnonama = input('Input nomor kolom untuk "Nama Sampel":')
        colnoalamat = input('Input nomor kolom untuk "Alamat Sampel":')
        

        ## Assign
        start = 1
        end = len(df)
        gagal = 0
        rowgada = 0
        ## jika gagal loop terus :""
        time.sleep(1)
        #notif.show_toast("Assign fasih PY", "I Need U to PRESS ENTER :(", duration = 1)
        #input("# PRESS ENTER to Start Assigning")
        
        print('\n# Start assigning fasih --- ')
        while True:
            ## loop per row daftar_assign csv
            try:
                for dfrow in range(start,end): ## loop row df
                    ## Search by idwilker
                    now = datetime.datetime.now()
                    print(f"{now}| {df.index[dfrow]-1}| {df.nm_sampel[dfrow]} |", end="")
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
                        print('kosong')
                        with open('Assign_fasih_log.csv','a', newline='') as fd:
                            writer = csv.writer(fd)
                            writer.writerow([df.index[dfrow]-1, now, df.alamat[dfrow], df.nm_sampel[dfrow], "tidak ada di fasih"])
                        continue
                        
                    ## Jumlah row yang ditampilin di fasih
                    #jml_row = 10+1
                    jml_row = int(driver.find_element_by_css_selector('div#assignmentDatatable_info').text.split()[3]) + 1
                    
                    for i in range(1,jml_row): ## loop row fasih, cek row yang diinginkan
                        ## cek nama kolom
                        headusersaatini = driver.find_elements_by_css_selector(f'.thead-bps td:nth-child({str(colnousersaatini)})')[0].text
                        if headusersaatini!="User Saat ini": raise Exception("Kolom sudah berubah, hubungi admin suruh sesuaikan lagiii")
                        
                        id_web = driver.find_elements_by_css_selector(f'.ng-star-inserted:nth-child({str(i)}) > .ng-star-inserted:nth-child({str(colnonama)})')[0].text + \
                            driver.find_elements_by_css_selector(f'.ng-star-inserted:nth-child({str(i)}) > .ng-star-inserted:nth-child({str(colnoalamat)})')[0].text
                        usersaatini = driver.find_elements_by_css_selector(f'.ng-star-inserted:nth-child({str(i)}) > td:nth-child({str(colnousersaatini)})')[0].text
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
                        print('ganemu, mungkin kosong')
                        with open('Assign_fasih_log.csv','a', newline='') as fd:
                            writer = csv.writer(fd)
                            writer.writerow([df.index[dfrow]-1, now, df.alamat[dfrow], df.nm_sampel[dfrow], "ganemu, mungkin tidak ada di fasih, ricek"])
                        continue
                    ## cek row matching and tick jika user saat ini masi ()
                    tick = 0
                    if (usersaatini !='()'): 
                        ## jika dah ke assign maka CONT
                        print('skip dah ke assign ke '+usersaatini)
                        ## write log
                        with open('Assign_fasih_log.csv','a', newline='') as fd:
                            writer = csv.writer(fd)
                            writer.writerow([df.index[dfrow]-1, now,df.alamat[dfrow], df.nm_sampel[dfrow], usersaatini, df.email_petugas[dfrow]])
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
                    print('sukses assign ke '+df.email_petugas[dfrow])
                    ## write log
                    with open('Assign_fasih_log.csv','a', newline='') as fd:
                        writer = csv.writer(fd)
                        writer.writerow([df.index[dfrow]-1, now,df.alamat[dfrow], df.nm_sampel[dfrow], usersaatini, df.email_petugas[dfrow]])

                print('SLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEESE')
                notif.show_toast("Assign fasih PY", "YEYYY SELESE :)", duration = 1)
                break
                            
            ## jika gagal print error
            except Exception as e:
                print('# Error terjadi: '+str(e))
                start = dfrow-1
                if start <0: start = 0
                gagal += 1
                print('# Gagal:',gagal)
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
                    driver.refresh()
                    time.sleep(5)
                    ########
                    ## !! Komen di bawah ini perlu jika tiap refresh bulan surveinya berbeda. or apalah ketentuannya
                    ########
                    #notif.show_toast("Assign fasih PY", "I Need U to MILIH SURVEY lagi :(", duration = 1)
                    print('# Refreshing')
                    print("# Restart lagi at row: ",start)
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'td.sorting_disabled:nth-child(2)')) )
                    continue
                if ((gagal >100) or (difftime<3)): #!! jika different time gagalnya gagal maka remove aja OR blabla nya
                    #Audio(sound_file, autoplay=True)
                    print("# Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))
                    notif.show_toast("Assign fasih PY", "ERROR HAPPEN :(", duration = 1)
                    raise Exception("# Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))
                    break
                print("# Restart lagi at row: ",start)
                continue
            
        ## play notif
        #Audio(sound_file, autoplay=True)
        input("CLOSE PROGRAMS")
       
    ## except all
    except Exception as e:
        print("\n# Error: "+str(e))
        notif.show_toast("Assign fasih PY", "ERROR HAPPEN :(", duration = 1)
        input("CLOSE AND RESTART")
