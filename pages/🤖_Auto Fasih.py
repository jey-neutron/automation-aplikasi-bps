# Library
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
import pandas as pd
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# import csv
import os
from os import walk
import sys
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html


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

# file program yang tersedia di folder directory
opt_modul = []
for (dirpath, dirnames, filenames) in walk( str(this_path)+r"/pages/code_new" , topdown=True):
    dirnames[:] = [d for d in dirnames if d not in set(['__pycache__'])]
    for filename in filenames:
        # only get .py file
        if ".py" in filename:
            opt_modul.append(filename.split(".")[0])
    #break
# get inside code directory to get desc each module
modul_desc = []
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'\code_new')
for modul_name in opt_modul:
    modul = __import__(modul_name)
    modul_desc.append(modul.desc())
modul_dict = dict(zip(opt_modul,modul_desc))  
opt_modul.insert(0, '-')

# session state init
if "var_submit" not in st.session_state:
    st.session_state.var_submit = 0


# HTML header
st.set_page_config(page_title="Auto Fasih", layout="wide", page_icon="🤖")
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
placehold_title = st.empty()
placehold_desc = st.empty()

cols = st.columns([3,1,1])
with cols[0]:
    opt_modul_selected = st.selectbox("Pilih yang ingin dikerjakan", options=opt_modul, index=0)#index=opt_modul.index('_Cek data terpilih'))    
with cols[1]:
    st.markdown(f'<p class="small-font">ㅤ</p>', unsafe_allow_html=True)
    pilihprog = st.button("🏇 Mulai",type="primary",use_container_width=True)
with cols[2]:
    st.markdown(f'<p class="small-font">ㅤ</p>', unsafe_allow_html=True)
    reset_form = st.button('🛖 Stop/Reset', use_container_width=True)
    if reset_form:
        st.session_state.var_submit = 0
        st.session_state.var_rentang = 1
next(sp0,None)


# Func buat Input form filter
def blok_form(sso=False, gsheet=False, survei=False, rentang=False, desc_rentang='Baris mana program mulai jalan/Kolom apa dimana (tergantung modul program terpilih) <br>- Isi 1 atau 0 berarti dari baris pertama <br>- Isi 1-6 berarti dari baris 1-6 <br>- Isi 4,5,7 berarti baris 4,5,7, Atau bisa juga kolom namasampel = 4 , alamat = 5, user saat ini = 7 <br> Lebih lanjut baca DESKRIPSI'):
    # init
    usernamesso=_EDIT.variabel['username']; passwordsso=_EDIT.variabel['password']; tabsurvei=''; pilihan_survei=_EDIT.variabel['survei_fasih']; df_name=_EDIT.variabel['sheetID']; sheet_name=_EDIT.variabel['sheetname']; rentang=_EDIT.variabel['rentang']
    
    # Form for sso
    if sso:
        twocol2 = st.columns(2)
        with twocol2[0]: #user sso
            usernamesso = st.text_input("Username SSO", value= st.session_state.var_usernamesso if "var_usernamesso" in st.session_state else _EDIT.variabel['username'])
        with twocol2[1]: #user pass
            passwordsso = st.text_input("Password SSO", value= st.session_state.var_passwordsso if "var_passwordsso" in st.session_state else _EDIT.variabel['password'], type="password")
        # st.markdown(
        #     f'<p class="small-font">Untuk mengubah "default value" dapat mengedit file <a>_EDIT.py</a> di folder ini: <a href="{str(this_path)}">{str(this_path)}</a></p>',
        #     unsafe_allow_html=True)
    
    # Form for read file csv used
    if gsheet:
        twocol2 = st.columns(2)
        with twocol2[0]: #Gsheet ID
            df_name = st.text_input("Google Sheet ID", disabled=True, value= st.session_state.var_df_name if "var_df_name" in st.session_state else _EDIT.variabel['sheetID'])
        with twocol2[1]: #sheet name
            sheet_name = st.text_input("Nama Sheet yang dipake",  value= st.session_state.var_sheet_name if "var_sheet_name" in st.session_state else _EDIT.variabel['sheetname'])
        linkgsheet = f"https://docs.google.com/spreadsheets/d/{df_name}"
        st.markdown(
            f'<p class="small-font">Masukkan Google Sheet ID dan Nama Sheet yang dipake untuk read data. Liat filenya di link ini: <a href="{linkgsheet}">Google Sheet</a></p>',
            unsafe_allow_html=True)
        
    # Form argumen modul
    if survei:
        twocol2 = st.columns([1,2])
        with twocol2[0]:
            tabsurvei = st.selectbox("Tab survei", options=['Pencacahan','Pelatihan','Uji Coba'], index=0)
        with twocol2[1]:
            pilihan_survei = st.text_input('Ketik nama survei di Fasih', value= st.session_state.var_pilihan_survei if "var_pilihan_survei" in st.session_state else _EDIT.variabel['survei_fasih'])
        st.markdown(
            f'<p class="small-font">Sementara input manual dulu :" DAN HARUS SAMA DI FASIH</p>',
            unsafe_allow_html=True)
        
    # Form rentang row yang ingin dijalankan
    if rentang:
        rentang = st.text_input('Rentang baris atau rentang kolom', value= st.session_state.var_rentang if "var_rentang" in st.session_state else 1)
    if desc_rentang:
        st.markdown( f'<p class="small-font">{desc_rentang}</p>'  , unsafe_allow_html=True )

    return usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang

# Input Form filter 
import _EDIT
@st.dialog ("Isi form ini dulu")
def open_form(modul_selected):
#with st.container().form(key="form_sso"):
    

    st.write("Baca deskripsi yah untuk ngisinya gimana aja")
    #st.session_state.var_rentang = 1
    if modul_selected=='_Cek data terpilih':
        #st.session_state.var_rentang = 0
        usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang = blok_form(desc_rentang='',gsheet=True)
    elif modul_selected=='Assign fasih by namalamat':
        if "var_rentang" not in st.session_state:    
            st.session_state.var_rentang = "4,5,7"
        usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang = blok_form(sso=True, gsheet=True, survei=True, rentang=True, desc_rentang='Isi X,Y,Z<br>X = kolom nama sampel | Y = kolom alamat | Z = kolom user saat ini<br>Kolom centang paling kiri adalah kolom 1')
    elif modul_selected=='Get data fasih SKTNP':
        st.session_state.var_pilihan_survei = 'SKTNP 2024'
        usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang = blok_form(sso=True, survei=True, rentang=True, desc_rentang='Isi 1 jika get all row <br> Isi X-Y untuk get data from row X sampe Y')
    elif modul_selected=='Get fasih sm rows sampel':
        usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang = blok_form(sso=True, survei=True, rentang=True, desc_rentang='Isi X akan get row number X <br> Isi X-Y untuk get data from row X sampe Y')
    elif modul_selected=='Isi laporan fasih sep':
        st.session_state.var_pilihan_survei = 'SURVEI PELAPORAN LAPANGAN SEP 2024'
        usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang = blok_form(sso=True, gsheet=True, survei=True, rentang=True, desc_rentang='Isi X berarti ngisi pada kecamatan X <br>- Isi X-Y berarti dari kecamatan X-Y <br>- Isi X,Y,Z berarti ngisi pada kecamatan X,Y,Z ')
    else:
        usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang = blok_form(sso=True, gsheet=True, survei=True, rentang=True)
    

    
    
    # submit
    #submit_form = 
    # if submit form filter
    if st.button("🏇 RUN Program", type="primary", use_container_width=True):
        st.session_state.var_submit = 1
        st.session_state.var_opt_modul_selected = modul_selected
        st.session_state.var_usernamesso = usernamesso
        st.session_state.var_passwordsso = passwordsso
        st.session_state.var_tabsurvei = tabsurvei
        st.session_state.var_pilihan_survei = pilihan_survei
        st.session_state.var_df_name = df_name
        st.session_state.var_sheet_name = sheet_name
        st.session_state.var_rentang = rentang
        st.rerun()
                

# PILIHAN VIEW HTML
if opt_modul_selected != '-':
#if pilihprog:
    with placehold_title:
        st.title("Autoin: "+opt_modul_selected)
    with placehold_desc:
        st.markdown(f'Deskripsi program: <span class="colororange">{modul_dict[opt_modul_selected].split(")")[1][:-1]}</span>'  , unsafe_allow_html=True) 
    st.markdown("#### Nama Auto-program yang tersedia beserta deskripsinya:")
    st.expander(f':orange[{opt_modul_selected}]', expanded=True).markdown(modul_dict[opt_modul_selected], unsafe_allow_html=True)

    # jika mencet tombol mulai, maka munculin dialog box
    if pilihprog:
        open_form(opt_modul_selected)
    
#elif "var_submit" in st.session_state:
elif st.session_state.var_submit == 1:
    # title page
            
    #from st_click_detector import click_detector
    #import streamlit.components.v1 as components
    st.session_state.var_submit = 0
    opt_modul_selected = st.session_state.var_opt_modul_selected
    usernamesso = st.session_state.var_usernamesso
    passwordsso = st.session_state.var_passwordsso
    tabsurvei = st.session_state.var_tabsurvei
    pilihan_survei = st.session_state.var_pilihan_survei
    df_name = st.session_state.var_df_name
    sheet_name = st.session_state.var_sheet_name 
    rentang = st.session_state.var_rentang
    
    # WELCOME TO AUTO FASIH
    with placehold_title:
        st.title("Autoin: "+opt_modul_selected)
    with placehold_desc:
        st.markdown(f'Deskripsi program: <span class="colororange">{modul_dict[opt_modul_selected].split(")")[1][:-1]}</span>'  , unsafe_allow_html=True) 
    # LALALLALA PR: nanti ada deskripsi di tiap2 program n rewrite program yak
    # PR: nanti ada tombol 'mulai', 'berhenti', start firefox masuk di 'mulai' ajde
    # PR: jika ada user input gimana? kek misal milih survei, notif gimana? perlukah parameter?
    # Pilih Program Auto with import method

    program_selected = __import__(opt_modul_selected)
    my_bar = st.progress(0, text=" Memulai program...")
    for i in range(100):
        time.sleep(0.03)
        my_bar.progress(i+1, text=" Memulai program...")
    time.sleep(0.2)
    my_bar.empty()
    # with st.spinner(" Loading... "):
    #     with st.empty():
    #         for i in range(3,0,-1):
    #             st.empty().code('Program dimulai dalam '+str(i))
    #             time.sleep(1)
    #         st.empty()

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
    logger = get_logger(program_selected.__name__)
    logger.handlers.clear()
    #handler = StreamlitLogHandler(st.code)
    handler = StreamlitLogHandler(write_log)
    logger.addHandler(handler) 


    # run program and display log
    sp = iter(make_spinner("Running programs..."))
    
    # log inline
    st.write('Hasil: ')
    next(sp)
    placeholder_loginline = st.empty()
    placeholder_result = st.empty()
    placeholder_download = st.empty()
    handlerst = StreamlitLogHandler(write_log_inline)
    logger.addHandler(handlerst)
    
    st.write("Log file history:")
    placeholder_log = st.container(height=500)
    #st.code(logger.callHandlers())
    try:
        hasil_run, df = program_selected.RUN(usernamesso, passwordsso, tabsurvei, pilihan_survei, df_name, sheet_name, rentang, headless = _EDIT.variabel['hide_firefox'], close_ff=_EDIT.variabel['close_firefox_on_error'])
        #with st.container(height=350):        
            #next(sp) # starts spin
        try:
            with placeholder_download:
                st.download_button(
                    label="Download log result as CSV",
                    data=df.to_csv().encode("utf-8"),
                    file_name=f"log_result {opt_modul_selected}_{pilihan_survei}.csv",
                    mime="text/csv",
                    use_container_width= True
                )
        except: pass
        with placeholder_result:
            if "Error" in hasil_run:
                st.error(hasil_run)
            else:
                st.success(hasil_run)
    finally:
        next(sp, None) #spin end
        #st.success("Automasi selesai dijalankan")
        
else:
    with placehold_title:
        st.title("🤖 Auto Fasih Bzzzz")
    with placehold_desc:
        st.write("Ngerjain Fasih web atau web BPS lain secara otomatis")
    #with placehold_desc2:
        #st.warning("Silakan mulai program dari sidebar")
    st.markdown("#### Nama Auto-program yang tersedia beserta deskripsinya:")
    with st.container(height=500):
        #st.write(modul_dict)
        #st.write(modul_dict.values())
        num = 0
        for key,val in zip(modul_dict.keys(), modul_dict.values()):
            num+=1
            st.expander(f':orange[{str(num)}- {key}]', expanded=True if key=='_Cek data terpilih' else False).markdown(val, unsafe_allow_html=True)

    #st.write({ 'dictA': {'key_1': 'value_1'},
    #        'dictB': {'key_2': 'value_2'}})