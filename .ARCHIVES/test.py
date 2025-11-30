from lib_srt import srt
from lib_translateLocally import translateLocally

# Functions
def run_translate(definition):
    my_srt = srt()
    my_tr = translateLocally() # preconfigured with binary and model
    if 'sub_in' not in definition:
        return -1
    if 'sub_out'  not in definition:
        return -2
    sub_len = len(definition['sub_in'])
    if sub_len != len(definition['sub_out']):
        return -3
    for cpt in range(0, sub_len):
        left = definition['sub_in'][cpt]
        right = definition['sub_out'][cpt]
        # HTML mode
        #left_html = left[:-3] + "en.html"
        #right_html = left[:-3] + "fr.html"
        #my_srt.srt_to_html(left, left_html)
        #my_tr.translate(left_html, right_html)
        #my_srt.html_to_srt(right_html, right)
        # TXT mode
        left_txt = left[:-3] + "en.txt"
        right_txt = left[:-3] + "fr.txt"
        my_tr.setFormat('txt')
        my_srt.srt_to_txt(left, left_txt)
        my_tr.translate(left_txt, right_txt)
        my_srt.txt_to_srt(right_txt, right)
        return

path="/mnt/d/"
worksheet = {
    # Lists for extraction
    'video_in': [],
    # Lists for translations
    'sub_in': [path+r"Venom.2018.1080p.UHD.BluRay.x265.HDR.DD5.1-Pahe.in2.srt"],
    'sub_out': [path+r"Venom.2018.1080p.UHD.BluRay.x265.HDR.DD5.1-Pahe.in.fr.srt"]
    }

# Ajouter  : les sous-titres extraits à la liste dans worksheet
run_translate(worksheet)

# Job done
print("Complete")