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
# Main View
# header html
st.set_page_config(page_title="Auto Fasih", page_icon="🤖")
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
        /*div[data-testid="stMarkdownContainer"] p{
            font-size: 100;
        }*/
        
        a#goto {
          background-color: rgb(255, 75, 75);
          box-shadow: 0 5px 0 darkred;
          color: white;
          padding: 0.3em 1em;
          position: relative;
          text-decoration: none;
          text-transform: uppercase;
        }

        a#goto:hover {
          background-color: #ce0606;
          cursor: pointer;
        }

        a#goto:active {
          box-shadow: none;
          top: 5px;
        }
    </style>
""", unsafe_allow_html=True) #css

# Input Form filter 
import _EDIT
twocol = st.columns(2)
with st.container(border=False):
    a = """
        opt_modul = []
        for (dirpath, dirnames, filenames) in walk( str(this_path)+r"/pages" , topdown=True):
            dirnames[:] = [d for d in dirnames if d not in set(['__pycache__','code_new'])]
            for filename in filenames:
                # only get .py file
                if ".py" in filename:
                    opt_modul.append(filename.split(".")[0])
            #break
        opt_modul_selected = st.selectbox("Pilih yang ingin dikerjakan", options=opt_modul)
        for modul_name in opt_modul:
            modul = __import__(modul_name)
            modul_desc.append(modul.desc())
        modul_dict = dict(zip(opt_modul,modul_desc))  
        opt_modul.insert(0, '-')
        
        st.title("🤖 Auto Fasih Bzzzz")
        st.caption("Ngerjain Fasih web atau web BPS lain secara otomatis")
        st.warning("Silakan mulai program dari sidebar")
        st.markdown("#### Nama Auto-program yang tersedia beserta deskripsinya:")
        with st.container(height=630):
            #st.write(modul_dict)
            #st.write(modul_dict.values())
            num = 0
            for key,val in zip(modul_dict.keys(), modul_dict.values()):
                num+=1
                st.expander(f':orange[{str(num)}- {key}]', expanded=True if key=='_Cek data terpilih' else False).markdown(val, unsafe_allow_html=True)
        #st.write({ 'dictA': {'key_1': 'value_1'},
        #        'dictB': {'key_2': 'value_2'}})
     """
    
    st.title("Feature:")
    st.subheader("🤖 Auto Fasih")
    with st.expander(":orange[Deskripsi]"):
        st.write('''
            Ngerjain kerjaan yang membutuhkan web Fasih atau web BPS lain secara otomatis. Jadi ga perlu manual satu per satu 👍. Tapi tergantung creator sih ada auto-nya ato ga (bisa request kak 📞).
        ''')
        #st.link_button("Go to page", "/Auto_Fasih")
        st.markdown('<a id="goto" href="/Auto_Fasih" target="_self">Go to App</a>',unsafe_allow_html=True)
        #st.image("https://static.streamlit.io/examples/dice.jpg")
        
    st.subheader("📝 Tulis Berita")
    with st.expander(":orange[Deskripsi]", expanded=True):
        st.write('''
            The chart above shows some numbers I picked for you.
            I rolled actual dice for these, so they're *guaranteed* to
            be random.
        ''')
        st.markdown('<a id="goto" href="/" target="_self">Go to App</a>',unsafe_allow_html=True)
        #st.image("https://static.streamlit.io/examples/dice.jpg")
        
    st.markdown("---")
    
    st.subheader("About")
    st.write("Nothing to see here. If u want to see, go to [Github](https://github.com/jey-neutron/)")
