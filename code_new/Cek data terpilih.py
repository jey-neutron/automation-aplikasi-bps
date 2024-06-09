import logging
import os
import sys
import time
import pandas as pd
from pathlib import Path

#config
logger = logging.getLogger(__name__)
this_path = Path().resolve()

# for main view func
def desc():
    # desc memuat keterangan program, sso buat apa, nama survei di fasih, dataframe used, rentang baris
    return "1) Program pendek untuk mengecek data csv terpilih \n 2) Juga terdapat template modul bagi developer (copy me) \n 3) Isi form terserah, kecuali data csv yang ingin dicek, lainnya ga ngaruh"

def RUN(ssoname, ssopass, pilihan_survei, df_name, rentang):
    try:
        # show warning in log
        logger.info("WARN: (Tes warning) Cek dulu df nya")
        #notif.show_toast("Auto fasih PY", "Cek df ya", duration = 1)
        # cek df
        if ".csv" in str(df_name):
            df = pd.read_csv(str(this_path)+"/"+df_name)
        elif ".xlsx" in str(df_name):
            df = pd.read_excel(str(this_path)+"/"+df_name, sheet_name=df_name.split(".")[0])
        logger.info(f'Details of data selected: \n- Filename = {str(df_name)} \n- In directory = {str(this_path)} \n- Size df = {len(df)} row x {len(df.columns)} columns \n- Columns = {[i for i in df.columns]}')
        logger.info(f"Data head =\n{df.head()}")
        # test START HERE

        # test 2
        time.sleep(1)
        logger.info("Hellow World 1")
        time.sleep(1)
        logger.info("Hellow World 2")
        time.sleep(1)
        # end test
        return("SLESEEEEE")
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.error('WARN: Error happen')
        #notif.show_toast("Auto fasih PY", "Error happen", duration = 1)
        return (f"Error: {str(e)}, type error: {exc_type}, on file: {fname} on line {exc_tb.tb_lineno}")