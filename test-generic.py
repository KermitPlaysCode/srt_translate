"""Test translators"""

from lib_translateArgos import TranslateArgos
from lib_translateLibreTranslate import TranslateLibreTranslate
from lib_translateLocally import TranslateLocally
from lib_srt import Srt
from lib_chrono import chrono

# Choose the engine
for mode in ['locally','argos','argos-cuda']: #,'libre']:

    timer = chrono()
    TO_TRANSLATE = r'D:/Restricted/Handbrake_entrée/lucifer/Lucifer.S04E01.en.srt'
    TO_TRANSLATE_TXT = TO_TRANSLATE[:-3 ]+'txt'
    TRANSLATED = r'D:/Restricted/Handbrake_entrée/lucifer/Lucifer.S04E01.'+mode+r'.fr.srt'
    TRANSLATED_TXT = TRANSLATED[:-3]+'txt'

    my_srt = Srt()
    tr = None
    if mode == 'locally':
        tr = TranslateLocally(executable=r'D:/temp/translateLocally.windows-2022.core-avx-i.exe')
    elif mode == 'argos':
        tr = TranslateArgos()
    elif mode == 'argos-cuda':
        tr = TranslateArgos(cuda=True)
    elif mode == 'libre':
        tr = TranslateLibreTranslate(uri='http://192.168.240.1:5000/')
    else:
        print("Wrong enfine selected")
        exit(-1)

    timer.start()
    print(f"=== MODE {mode}===")
    my_srt.srt_to_txt(TO_TRANSLATE, TO_TRANSLATE_TXT)
    x = tr.translate(
        file_in = TO_TRANSLATE_TXT,
        file_out = TRANSLATED_TXT
    )
    my_srt.txt_to_srt(input_txt=TRANSLATED_TXT, output_srt=TRANSLATED)
    timer.stop()
    my_srt.cleanup_txt()
    print("Result of translation:",x)
    print("Time to execute:", str(timer.get_time()))
