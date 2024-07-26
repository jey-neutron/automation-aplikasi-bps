# Library idx
import time
import datetime
import pandas as pd
import os
from os import walk
import sys
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html
# Library pages
import logging
import pandas as pd
from pathlib import Path
import csv
import _EDIT

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
        # Library pages #2 biar gaberat
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        # to stale
        from selenium.common.exceptions import NoSuchElementException
        from selenium.common.exceptions import StaleElementReferenceException
        from selenium.webdriver.support import expected_conditions

        df = ''
        logger.info('lellele')
        return "ole"
        # Open mozilla
        logger.info("Opening mozilla ")
        driver = _EDIT.open_ff(headless=False)
        # add option mozilla
        # opts = webdriver.FirefoxOptions()
        # opts.add_argument("--width=1000")
        # opts.add_argument("--height=800")
        # #opts.headless = True
        # # add profile extension automa
        # profile = webdriver.FirefoxProfile() 
        # if Path("../automa-1.28.27.xpi").is_file():
        #     logger.info("with added extension")
        #     profile.add_extension(extension='../automa-1.28.27.xpi')
        # driver = webdriver.Firefox(executable_path = str(this_path)+"/"+"geckodriver.exe", firefox_profile=profile, options=opts)

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
    

# HTML VIEW
# config
import warnings
warnings.filterwarnings("ignore")
# init spin
def make_spinner(text="Loading..."):
    with st.spinner(text):
        yield
sp0 = iter(make_spinner("Loading programs..."))
this_path = Path().resolve()
# logging (use logger.info di anaknya instead of print)
import logging
from streamlit.logger import get_logger

class StreamlitLogHandler(logging.Handler):
    def __init__(self, widget_update_func):
        super().__init__()
        self.widget_update_func = widget_update_func

    def emit(self, record):
        msg = self.format(record)
        self.widget_update_func(msg)

# header html
next(sp0) # start spin on load web
st.markdown("""
    <style>
        .small-font {
            font-size:12px;
            font-style: italic;
            color: #b1a7a6;
        }
        .colororange{
            color: #fd971f;
        }
        .pre{
            font-family: monospace;
            font-size: 14px;
            color: #b1a7a6;
        }
        .stCodeBlock{
            border-color: red
        }
        .note{
            border-radius: 0.2em;
            background-color: #ff4b4b;
            font-weight:bold;
        }
    </style>
""", unsafe_allow_html=True) #css


# MAIN VIEW
# WELCOME TO AUTO FASIH
opt_modul_selected = "🧾 Get Fasih-SM Rows Sampel"
st.title("Autoin: "+opt_modul_selected)
st.markdown(f'Deskripsi program: <span class="colororange">{desc().split(")")[1][:-1]}</span>'  , unsafe_allow_html=True) 
placeholder_load = st.empty()
placeholder_loginline = st.empty()
placeholder_hasildownload = st.empty()
placeholder_hasil2 = st.empty()
# title v
# deskripsi v
# tombol log stop/reset
# latest log v
# baru log history v

st.markdown("""---""")
twocol = st.columns(2)
# Kolom 1 for Input Form filter 
with twocol[0].container():

    # Form for read file csv used
    twocol2 = st.columns(2)
    with twocol2[0]: #Gsheet ID
        df_name = st.text_input("Google Sheet ID", _EDIT.sso_pegawai['sheetID'])
    with twocol2[1]: #sheet name
        sheet_name = st.text_input("Nama Sheet",  _EDIT.sso_pegawai['sheetname'])
    linkgsheet = f"https://docs.google.com/spreadsheets/d/{df_name}"
    st.markdown(
        f'<p class="small-font">Masukkan Google Sheet ID dan Nama Sheet yang dipake untuk read data. Liat filenya di link ini: <a href="{linkgsheet}">Google Sheet</a></p>',
        unsafe_allow_html=True,
    )


    #reset_form = st.button('🛖 Stop/Reset', key='home', use_container_width=True)
    with st.container().form(key="form_sso"):
        # submit
        submit_form = st.form_submit_button("🏇 RUN Program", type="primary", use_container_width=True)

        #st.subheader("Isi form ini dulu")
        # Form for read file csv used
        twocol2 = st.columns(2)
        with twocol2[0]: #Gsheet ID
            usernamesso = st.text_input("Username SSO", _EDIT.sso_pegawai['username'])
        with twocol2[1]: #sheet name
            passwordsso = st.text_input("Password SSO", _EDIT.sso_pegawai['password'], type="password")
        st.markdown(
            f'<p class="small-font">Untuk mengubah "default value" dapat mengedit file <a>_EDIT.py</a> di folder ini: <a href="{str(this_path)}">{str(this_path)}</a></p>',
            unsafe_allow_html=True,
        )
        
        # file program yang tersedia di folder directory
        opt_modul = []
        for (dirpath, dirnames, filenames) in walk( str(this_path)+r"/code_new" , topdown=True):
            dirnames[:] = [d for d in dirnames if d not in set(['__pycache__'])]
            for filename in filenames:
                # only get .py file
                if ".py" in filename:
                    opt_modul.append(filename.split(".")[0])
            #break
        opt_modul_selected = st.selectbox("Pilih yang ingin dikerjakan", options=opt_modul, index=opt_modul.index('_Cek data terpilih'))
        st.markdown(
            f'<p class="small-font">Baca deskripsi program di view utama</p>',
            unsafe_allow_html=True,
        )
        # get inside code directory to get desc each module
        modul_desc = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(dir_path+'/code_new')
        for modul_name in opt_modul:
            modul = __import__(modul_name)
            modul_desc.append(modul.desc())
        modul_dict = dict(zip(opt_modul,modul_desc))  

        # argumen modul
        pilihan_survei = st.text_input('Ketik nama survei di Fasih', _EDIT.sso_pegawai['survei_fasih'])
        st.markdown(
            f'<p class="small-font">Sementara input manual dulu :" <br> DAN HARUS SAMA DI FASIH</p>',
            unsafe_allow_html=True,
        )

        # rentang row yang ingin dijalankan
        rentang = st.text_input('Rentang baris atau rentang kolom', 1)
        st.markdown(
            f'<p class="small-font">Baris mana program mulai jalan/Kolom apa dimana (tergantung modul program terpilih) <br>- Isi 1 atau 0 berarti dari baris pertama <br>- Isi 1-6 berarti dari baris 1-6 <br>- Isi 4,5,7 berarti baris 4,5,7, Atau bisa juga kolom namasampel = 4 , alamat = 5, user saat ini = 7 <br> Lebih lanjut baca DESKRIPSI</p>',
            unsafe_allow_html=True,
        )
        
    #st.markdown("[top](#isi-form-ini-dulu)", unsafe_allow_html=True)
    #reset_form = st.button('🛖 Stop/Reset', key='home', use_container_width=True)
    #st.button('goto', on_click=goto, args=('#isi-form-ini-dulu',))

# Kolom 2 container for log result
with twocol[1].container():    
    # if submit form filter
    next(sp0,None)
    st.write("Log file history:")
    reset_form = st.button('🛖 Stop/Reset', key='home', use_container_width=True)
    placeholder_log = st.container(height=500) #container for log
    
    if submit_form:
        program_selected = __import__(opt_modul_selected)
        with placeholder_load:
            my_bar = st.progress(0, text=" Memulai program...")
            for i in range(100):
                time.sleep(0.03)
                my_bar.progress(i+1, text=" Memulai program...")
            time.sleep(0.2)
            my_bar.empty()

        # cek if file temp exist (yah buat pengganti notifikasi ajasi #blm berhasil)
        def cek_input(namafile='temp_input.txt'):
            if Path(str(this_path)+f"/{namafile}").exists():
                return True # berarti ada suruh nginput
            
        # try cuztomize writing log 
        def write_log(logtext):
            with placeholder_log:
                if 'CONFIRM_DELETE' in logtext:
                # GAGAL WORK, LANJUT AJA LA
                    txt = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext).split(':')[1]}"
                    st.warning(txt)
                    # st.warning("Click button di bawah")        
                #     b = st.checkbox("Tick me jika sudah ngecek Firefox")
                #     b = st.button('Click', key='cek_input')        
                #     if b:
                #         os.remove((this_path)+f"/temp_input.txt")
                #         b = st.checkbox("Tick me jika sudah ngecek Firefox", disabled=True)
                    return()
                #if 'WARN' in logtext:
                #    return st.warning(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext).split(':')[1]}")
                elif 'DF' in logtext:
                    return st.text(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext).split('=')[1]}")
                txt = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext)}"
                #logs_data.append(txt)
                return st.markdown(f'<div class="pre">{txt}</div>', unsafe_allow_html=True)
            
        def write_log_inline(logtext):
            with placeholder_loginline:
                if 'WARN' in logtext:
                    return st.warning(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext).split(':')[1]}")
                return st.code(f"LATEST LOG: {datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext)}")

        # loging code
        logger = get_logger(__name__)
        logger.handlers.clear()
        #handler = StreamlitLogHandler(st.code)
        handler = StreamlitLogHandler(write_log)
        logger.addHandler(handler) 


        # run program and display log
        sp = iter(make_spinner("Running programs..."))
        
        # log inline
        with placeholder_load:
            next(sp)
        handlerst = StreamlitLogHandler(write_log_inline)
        logger.addHandler(handlerst)
        
        #st.code(logger.callHandlers())
        
        try:
            hasil_run, df = RUN(usernamesso, passwordsso, pilihan_survei, df_name, sheet_name, rentang, close_ff=_EDIT.sso_pegawai['close_firefox_on_error'])
            #with st.container(height=350):        
                #next(sp) # starts spin
            try:
                with placeholder_hasildownload:
                    st.download_button(
                        label="Download log result as CSV",
                        data=df.to_csv().encode("utf-8"),
                        file_name=f"log_result {opt_modul_selected}_{pilihan_survei}.csv",
                        mime="text/csv",
                        use_container_width= True
                    )
            except: pass
            if "Error" in hasil_run:
                with placeholder_hasil2:
                    st.error(hasil_run)
            else:
                with placeholder_hasil2:
                    st.success(hasil_run)
        finally:
            next(sp, None) #spin end
            #st.success("Automasi selesai dijalankan")        

    else:
        with placeholder_log:
            st.markdown(f'<div class="pre">Tidak ada aktivitas log</div>', unsafe_allow_html=True)
            
 