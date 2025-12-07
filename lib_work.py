"""Functions to prepare and execute extract and translate tasks"""

# file types
from os.path import isdir,isfile
from os.path import join as pathjoin
from os import listdir

from lib_ffmpeg_subs import FfmpegExtractSubs
from lib_srt import Srt
from lib_translateLocally import TranslateLocally
from lib_translateArgos import TranslateArgos
from lib_translateLibreTranslate import TranslateLibreTranslate
import config_cli

# Error codes
ERR_OK = 0
ERR_INVALID_FOLDER = -1
ERR_NO_SUBS_FILE = -2
ERR_SRT_TO_TXT = -3
ERR_TRANSLATE = -4
ERR_TXT_TO_SRT = -5

class _fake():
    def translate(self, x, y):
        """Fake function to initialize Work"""
        x,y = y,x
        return ""

class Work:
    """Manage tasks for extarct and translate"""

    def __init__(self):
        """Constructor"""
        self.go = True
        self._engine = _fake()

    def prepare_work(self, cli_args):
        """Get command line arguments and prepare work lists"""
        di = getattr(cli_args, 'input_video')
        do = getattr(cli_args, 'output_srt')
        tr = getattr(cli_args, 'translate')
        ex = getattr(cli_args, 'extract')
        fi = getattr(cli_args, 'input_sub')
        fo = getattr(cli_args, 'output_sub')
        xl = getattr(cli_args, 'engine')
        uri = getattr(cli_args, 'uri') # for libretranslate
        # Choose engine
        if xl == 'libretranslate':
            self._engine = TranslateLibreTranslate(uri)
        elif xl == 'locally':
            self._engine = TranslateLocally()
        else:
            self._engine = TranslateArgos(cuda=True)

        # Default/preferred action : translate
        if ex and tr:
            ex = False
        if not ex and not tr:
            tr = True
        response = {
            # Lists for work
            'in_dir': "",
            'out_dir': "",
            'files': [],
            # Action flags
            'translate': tr,
            'extract': ex
        }
        # Select input1
        if fi is not None:
            if fo is None:
                fo = fi[:-3] + "fr.srt"
            response['in_dir'] = ''
            response['out_dir'] = ''
            response['translate'] = True
            response['extract'] = False
            response['files'] = [fi]
            response['unique_srt_out'] = fo
        else:
            if do is None:
                do = di
            response['in_dir'] = di
            response['out_dir'] = do
            if ex:
                response['files'] = self.get_from_dir(di, config_cli.VIDEOS)
            if tr:
                response['files'] = self.get_from_dir(di, config_cli.SUBS)
        return response

    def update_work(self, ws, sl):
        """Add subs to the list after an extraction
        ws = worksheet
        sl = subs list got from extraction
        """
        ws['in_dir'] = ws['out_dir']
        ws['files'] = sl
        return ws

    def get_from_dir(self, folder, extensions):
        """Get a list of mp4 and mkv files in the provided folder"""
        list_files = []
        if isdir(folder):
            tmp = listdir(folder)
            for entry in tmp:
                entry_fullpath = pathjoin(folder, entry)
                if isfile(entry_fullpath) and entry.lower().endswith(extensions):
                    list_files.append(entry)
        return list_files

    def run_extract(self, definition):
        """Extract subs from videos"""
        ff_subs = FfmpegExtractSubs(config_cli.FFMPEG_PATH)
        subs_list = []
        print("Subs extracted:")
        for file in definition['files']:
            file_in = pathjoin(definition['in_dir'], file)
            file_out = pathjoin(definition['out_dir'], file[:-3]+'srt')
            r = ff_subs.extract(source=file_in, destination=file_out, lang='', test=False)
            if r != FfmpegExtractSubs.E_NO_ERROR:
                print(f"Error stream not found; e={r}")
            print(f"   - {file_out}")
            subs_list.append(file_out)
        return subs_list

    def _p(self, txt:str):
        print("lib_work: " + txt)
        return

    def run_translate(self, definition):
        """Execute translations as defined"""
        my_srt = Srt()
        sub_len = len(definition['files'])
        for cpt in range(0, sub_len):
            self._p(f"[{cpt}] {definition['files'][cpt]}")
            left = pathjoin(definition['in_dir'], definition['files'][cpt])
            right = pathjoin(definition['out_dir'], definition['files'][cpt][:-3]+'fr.srt')
            left_conv = left[:-3] + "en.txt"
            if sub_len == 1 and 'unique_srt_out' in definition:
                right_conv = definition['unique_srt_out']
            else:
                right_conv = left[:-3] + "fr.txt"
            # Step 1: convert srt to txt, stop if output file doesn't exist
            self._p(f"  - srt to txt {(left, left_conv)}")
            my_srt.srt_to_txt(left, left_conv)
            if not isfile(left_conv):
                self._p("  - Failed")
                return ERR_SRT_TO_TXT
            # Step 2: treanslate txt, stop if output file doesn't exist
            self._p(f"  - translate {(left_conv, right_conv)}")
            self._engine.translate(left_conv, right_conv)
            if not isfile(right_conv):
                self._p("  - Failed")
                return ERR_TRANSLATE
            # Step 3: convert txt to srt, stop if output file doesn't exist
            self._p(f"  - txt to srt {(right_conv, right)}")
            my_srt.txt_to_srt(right_conv, right)
            if not isfile(right):
                self._p("  - Failed")
                return ERR_TXT_TO_SRT
        my_srt.cleanup_txt()
        return ERR_OK
