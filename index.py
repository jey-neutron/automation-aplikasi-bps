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


# config
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
# Main View
# header html
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
    </style>
""", unsafe_allow_html=True) #css

# Input Form filter 
import _EDIT
twocol = st.columns(2)
with twocol[0].container():
    with st.container().form(key="form_sso"):
        st.subheader("Isi form ini dulu")
        st.write("Baca deskripsi di samping yah untuk milih mana aja")
        usernamesso = st.text_input("Username SSO", _EDIT.sso_pegawai['username'])
        passwordsso = st.text_input("Password SSO", _EDIT.sso_pegawai['password'], type="password")
        st.markdown(
            f'<p class="small-font">Untuk mengubah "default value" dapat mengedit file <a>_EDIT.py</a> di folder ini: <a href="{str(this_path)}">{str(this_path)}</a></p>',
            unsafe_allow_html=True,
        )
        
        # df name
        #df = pd.read_excel("../assign_cawi.xlsx", sheet_name="assign_cawi")
        opt_dfname = []
        for (dirpath, dirnames, filenames) in walk( str(this_path), topdown=True):
            dirnames[:] = [d for d in dirnames if d not in set(['__pycache__','.venv','.vscode','code','code_new'])]
            for filename in filenames:
                # only get .py file
                if ((".xlsx" in filename) or ('csv' in filename)):
                    opt_dfname.append(filename)
            #break
        df_name = st.selectbox("Pilih dataframe yang digunakan", options=opt_dfname, index=0)
        st.markdown(
            f'<p class="small-font">Edit dulu filenya di folder ini: <a href="{str(this_path)}">{str(this_path)}</a></p>',
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
        rentang = st.text_input('Opsional rentang baris atau rentang kolom', 1)
        st.markdown(
            f'<p class="small-font">Baris mana program mulai jalan/Kolom apa dimana (tergantung modul program terpilih) <br>- Isi 1 atau 0 berarti dari baris pertama <br>- Isi 1-6 berarti dari baris 1-6 <br>- Isi 4,5,7 berarti baris 4,5,7, Atau bisa juga kolom namasampel = 4 , alamat = 5, user saat ini = 7 <br> Lebih lanjut baca DESKRIPSI</p>',
            unsafe_allow_html=True,
        )
        # submit
        submit_form = st.form_submit_button("🏇 RUN Program", type="primary", use_container_width=True)

    reset_form = st.button('🛖 Stop/Reset', key='home', use_container_width=True)

with twocol[1].container():    
    # if submit form filter
    next(sp0,None)
    if submit_form:
        # title page
            
        #from st_click_detector import click_detector
        #import streamlit.components.v1 as components
        
        # WELCOME TO AUTO FASIH
        st.caption(f'Hellow "{usernamesso.split(".")[0]}", kamu memilih: ')
        st.title("Autoin: "+opt_modul_selected)
        st.markdown(f'Deskripsi program: <span class="colororange">{modul_dict[opt_modul_selected].split(")")[1][:-1]}</span>'  , unsafe_allow_html=True) 
        # LALALLALA PR: nanti ada deskripsi di tiap2 program n rewrite program yak
        # PR: nanti ada tombol 'mulai', 'berhenti', start firefox masuk di 'mulai' ajde
        # PR: jika ada user input gimana? kek misal milih survei, notif gimana? perlukah parameter?
        # Pilih Program Auto with import method

        program_selected = __import__(opt_modul_selected)
        with st.spinner(" Loading... "):
            with st.empty():
                for i in range(3,0,-1):
                    st.empty().code('Program dimulai dalam '+str(i))
                    time.sleep(1)
                st.empty()

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
                if 'WARN' in logtext:
                    return st.warning(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {str(logtext).split(':')[1]}")
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
        cols = st.columns(4)
        with cols[0]:
            #st.markdown('#### Log file:')
            downlog = st.button('Log file:', use_container_width=True, disabled=True) #PR: nanti buat download logfile
        #with cols[2]:
        with cols[1]:
            st.button('🛖 Stop/Reset', key='hometoo', use_container_width=True)
        
        # log inline
        next(sp)
        placeholder_loginline = st.empty()
        handlerst = StreamlitLogHandler(write_log_inline)
        logger.addHandler(handlerst)
        
        st.write("Log file history:")
        placeholder_log = st.container(height=490)
        #st.code(logger.callHandlers())
        try:
            hasil_run = program_selected.RUN(usernamesso, passwordsso, pilihan_survei, df_name, rentang, close_ff=_EDIT.sso_pegawai['close_firefox_on_error'])
            #with st.container(height=350):        
                #next(sp) # starts spin
            if "Error" in hasil_run:
                st.error(hasil_run)
            else:
                st.success(hasil_run)
        finally:
            next(sp, None) #spin end
            #st.success("Automasi selesai dijalankan")        


            
            
    else:
        st.title("🤖 Auto Fasih Bzzzz")
        st.caption("Ngerjain Fasih web atau web BPS lain secara otomatis")
        st.warning("Silakan mulai program dari sidebar")
        st.markdown("#### Nama Auto-program yang tersedia beserta deskripsinya:")
        with st.container(height=630):
            st.write(modul_dict)
        #st.write({ 'dictA': {'key_1': 'value_1'},
        #        'dictB': {'key_2': 'value_2'}})
