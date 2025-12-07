"""Streamlit interface to translate SRT subs"""

from os import remove #, system
from random import randint
import zipfile
import streamlit as st
from lib_srt import Srt
from lib_translateLocally import TranslateLocally
from lib_translateLibreTranslate import TranslateLibreTranslate
from lib_translateArgos import TranslateArgos

# Raise translator based on engine choice // default argos
if 'engine' in st.session_state and 'translator' not in st.session_state:
    e = st.session_state['engine']
    if e == 'locally':
        st.session_state['translator'] = TranslateLocally()
    elif e == 'libretranslate':
        st.session_state['translator'] = TranslateLibreTranslate(uri='https://127.0.0.1:5000')
    else:
        st.session_state['translator'] = TranslateArgos()

def zip_and_delete(list_files):
    """Zip a list of files then delete them"""
    tgt_zip = f'srt_translated_{str(randint(1000000, 9999999))}.zip'
    zipper = zipfile.ZipFile(file=tgt_zip,mode='w', compression=9, compresslevel=9)
    for file in list_files:
        zipper.write(file)
        remove(file)
    zipper.close()
    #cmd = "zip -9 " + tgt_zip + ' ' + ' '.join(list_files)
    #system(cmd)
    #for file in list_files:
    #    remove(file)
    return tgt_zip

# Page layout
# - page config
st.set_page_config(
    page_title='SRT translator with translateLocally',
    page_icon=':shark:',
    layout='wide'
)

# if needed
tab_in, tab_out = st.columns(2)
output_list = []
with tab_in:
    st.markdown(
        "# SRT translator")
    st.radio(
        label="Translate engine",
        options=['argos','libretranslate','translateLocally'],
        key='engine'
        )
    up_srt = st.file_uploader(
        "Send SRT file in english",
        type=None,
        accept_multiple_files=True,
        help="Upload SRT files in english"
    )

    if len(up_srt) > 0:
        for us in up_srt:
            input_srt = us.name
            input_txt = us.name[:-4] + '.txt'
            output_txt = input_txt[:-4] + '.fr.txt'
            output_srt = output_txt[:-4] + '.srt'
            tab_out.write([input_srt, input_txt, output_txt, output_srt])
            my_srt = Srt()
            with open(input_srt, "w", encoding="utf-8") as fout:
                fout.write(us.getvalue().decode('utf-8'))
            my_srt.srt_to_txt(input_srt, input_txt)
            st.session_state['translator'].translate(input_txt, output_txt)
            my_srt.txt_to_srt(output_txt, output_srt)
            del my_srt
            remove(input_srt)
            remove(input_txt)
            remove(output_txt)
            output_list.append(output_srt)

with tab_out:
    st.write("Fichier traduits :")
    if len(output_list) > 0:
        for x in output_list:
            st.write(x)
        zip_file = zip_and_delete(output_list)
        st.write("ZIP = ",zip_file)
        with open(zip_file, "rb") as fin:
            st.download_button(
                label='Download ZIP result',
                mime='application/zip',
                file_name=zip_file,
                data=fin)
