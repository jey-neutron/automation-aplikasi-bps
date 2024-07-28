## UBAH YANG PERLU ##

import os
import sys

# get path to file
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/code')
    
try:
    ## UBAH SSO PEGAWAI ##
    variabel = {
        "username" : "ssouser",
        "password" : "ssopass",
        "survei_fasih": "SAKERNAS 2024 AGS - PEMUTAKHIRAN",
        "sheetID":"1O0OUJkeGBJMTVeQ1MRLkYzGWCRqWGHyYBtDv4l-DK9I",
        "sheetname": 'Sheet1',
        "rentang":'1',
        "close_firefox_on_error" : True,
        "hide_firefox": False
    }
    """
    ## UBAH YANG MANA PY YANG MAU DI RUN ##
    py = 0
    # Pilihan program PY:
    # 1 = Assign fasih by nama & alamat
    # 2 = Assign fasih by id wilkerstat
    # 3 = Get fasih sm (SKTNP)
    # 4 = Get fasih sm (ident PODES)
    
    if py==1:
        import Assign_fasih_by_namalamat
        Assign_fasih_by_namalamat.RUN()
    elif py==2:
        import Assign_fasih_by_idwilker
        Assign_fasih_by_idwilker.RUN()
    elif py==3:
        import Get_fasih_sm_SKTNP
        Get_fasih_sm_SKTNP.RUN()
    elif py==4:
        import Get_fasih_sm_IDENTPODES
        Get_fasih_sm_IDENTPODES.RUN()
    input()
    """
    # Func to Open mozilla
    def open_ff(headless = variabel["hide_firefox"]):
        from selenium import webdriver
        from pathlib import Path
        # add option mozilla
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--width=1000")
        opts.add_argument("--height=800")
        opts.headless = headless
        # add profile extension automa
        profile = webdriver.FirefoxProfile() 
        if Path("../automa-1.28.27.xpi").is_file():
            profile.add_extension(extension='../automa-1.28.27.xpi')
        driver = webdriver.Firefox(executable_path = str(Path().resolve())+"/"+"geckodriver.exe", firefox_profile=profile, options=opts)

        return driver

except Exception as e:
    print('ERRR: ',str(e))
    input()
