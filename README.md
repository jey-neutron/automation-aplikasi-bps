# automation-aplikasi-bps
Beberapa code untuk mengautomatisasi pekerjaan yang menggunakan aplikasi BPS berbasis web dengan **Selenium Python** [pake OS windows sih]
<br>Contoh:
- Get data dari FASIH-SM Review
- Assign FASIH-SM by selection

Tinggal edit beberapa di file [`_EDIT.py`](/_EDIT.py) lalu jalankan [`_RUN.bat`](/_RUN.bat)

> *Update terbaru (06/24) make tampilan web di localhost. Sementara belum semua fitur/modul tersedia si. Tinggal jalankan [`_RUN.bat`](/_RUN.bat) trus ngisiin beberapa field yang diperlukan.
> - [`_run_alt.bat`](/_run_alt.bat) is using [`_code`](/code)
> - [`_RUN.bat`](/_RUN.bat) is using [`_code_new`](/code_new) *this is updated new, use this instead

## BEBERAPA FITUR/CODE ###
1. Ambil data row sampel di fasih
2. Ambil data Fasih Review survei SKTNP (blm update)
3. Ambil data Fasih Review Identifikasi SLS PODES (blm update)
4. Assign by Selection Fasih menggunakan nama dan alamat sampel (blm update)
5. Assign by Selection Fasih menggunakan ID Wilkerstat (blm update)
6. Pelaporan SEP di fasih

## BEBERAPA REQUIREMENT ###

### - req file (MUST NEED)
- [python](https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe)
- [mozilla](https://www.mozilla.org/firefox/download/thanks/) & [geckodriver](/geckodriver.exe)
- [assign_daftar.csv](/assign_daftar.csv) (untuk auto-assignment fasih)

### - req library python 
<sup>(abaikan, nanti auto keinstall ketika nge-run/open .py. Tapi kalo stuck install loop, re-run aja :")</sup>
- selenium==3.141.0
- pandas
- urllib3==1.26.16
- win10toast

### - assign_daftar.csv column:
- ID_Wilkerstat
- nm_sampel
- alamat
- email_petugas
- usersso_pengawas
