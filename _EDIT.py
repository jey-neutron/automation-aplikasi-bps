## UBAH YANG PERLU ##

import os
import sys
# get path to file
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/code')
    
try:
    ## UBAH SSO PEGAWAI ##
    sso_pegawai = {
        "username" : "usernamessopegawai",
        "password" : "passwordssopegawai"
    }
    
    ## UBAH YANG MANA PY YANG MAU DI RUN ##
    py = 4
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
    
except Exception as e:
    print('ERRR: ',str(e))
    input()
