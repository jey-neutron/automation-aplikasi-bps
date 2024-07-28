import logging
import os
import sys
import time
import pandas as pd
from pathlib import Path
import requests
from io import BytesIO

#config
import _EDIT
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
# func cek if needed an input, (we do it in alt way: write temp, trus jika user input, maka delete temp tersebut )
def writetemp_input(text):
    #with os.fdopen(fd, 'w') as tmp:
    with open('temp_input.txt','w') as tmp:
        tmp.write(text)
def cektemp_input(namafile='temp_input.txt'):
    if Path(str(this_path)+f"/{namafile}").exists():
        return True # berarti ada suruh nginput
def deltemp_input(namafile='temp_input.txt'):
    if Path(str(this_path)+f"/{namafile}").exists():
        return os.remove(str(this_path)+f"/{namafile}")

# for main view func
def desc():
    # desc memuat keterangan program, sso buat apa, nama survei di fasih, dataframe used, rentang baris
    return "1) Program pendek untuk mengecek data csv terpilih \n 2) Juga terdapat template modul bagi developer (copy me) \n 3) Isi form sesuai data yang ingin dicek, field Rentang ga ngaruh"

def RUN(ssoname, ssopass, pilihan_survei, df_name,sheet_name, rentang, close_ff=True):
    try:
        # show warning in log
        logger.info("WARN: (Tes warning) Cek dulu df nya")
        #notif.show_toast("Auto fasih PY", "Cek df ya", duration = 1)
        # cek df
        # if ".csv" in str(df_name):
        #     df = pd.read_csv(str(this_path)+"/"+df_name)
        #     df.loc[df.usersso_pengawas.str.contains('@bps.go.id'), 'usersso_pengawas'] = df.usersso_pengawas.str.strip('@')[0]
        #     onsheet = ''
        # elif ".xlsx" in str(df_name):
        #     df = pd.read_excel(str(this_path)+"/"+df_name, sheet_name=df_name.split(".")[0])
        #     onsheet = f" onsheet: {df_name.split(".")[0]} "
        url = f"https://docs.google.com/spreadsheets/d/{df_name}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        try:
            df = pd.read_csv(url, on_bad_lines='skip')
        except:
            df = ''
        
        logger.info(f'Details of data selected: <br>- GsheetID : {str(df_name)}, onsheet: {sheet_name}<br>- Directory work: {str(this_path)} <br>- Size df : {len(df)} row x {len(df.columns)} columns <br>- Columns : {[i for i in df.columns]} <br>')
        logger.info(f"DF= Data head :\n{df.head()}")
        # test START HERE

        # test END HERE
        # test 2
        time.sleep(1)
        logger.info("Hellow World 1")
        time.sleep(1)
        logger.info("Hellow World 2")
        time.sleep(1)
        # end test
        return("Program selesai di jalankan. NOTE!!!!! Kalo download result, bakalan langsung ke page home", df)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.error('WARN: Error happen')
        notif.show_toast("Auto fasih PY", "Error happen", duration = 1)
        #if close_ff:
        #    try:
        #        driver.close()
        #    except:
        #        pass
        return (f"Error: {str(e)}, type error: {exc_type}, on file: {fname} on line {exc_tb.tb_lineno}. NOTE!!!!! Bisa download result, tapi bakalan langsung ke page home", df)
