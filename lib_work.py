"""Functions to prepare and execute extract and translate tasks"""

# file types
from os.path import isdir,isfile
from os.path import join as pathjoin
from os import listdir

from lib_ffmpeg_subs import FfmpegExtractSubs
from lib_srt import srt
from lib_translateLocally import translateLocally
import config_cli

# Error codes
ERR_INVALID_FOLDER = -1
ERR_NO_SUBS_FILE = -2

class Work:
    """Manage tasks for extarct and translate"""

    def __init__(self):
        """Constructor"""
        self.go = True

    def prepare_work(self, cli_args):
        """Get command line arguments and prepare work lists"""
        di = getattr(cli_args, 'input_video')
        do = getattr(cli_args, 'output_srt')
        tr = getattr(cli_args, 'translate')
        ex = getattr(cli_args, 'extract')
        fi = getattr(cli_args, 'input_sub')
        fo = getattr(cli_args, 'output_sub')
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
        for file in definition['files']:
            file_in = pathjoin(definition['in_dir'], file)
            file_out = pathjoin(definition['out_dir'], file[:-3]+'srt')
            r = ff_subs.extract(source=file_in, destination=file_out, lang='', test=False)
            if r != FfmpegExtractSubs.E_NO_ERROR:
                print(f"Error stream not found; e={r}")
            print(f"  => output sub in {file_out}")
            subs_list.append(file_out)
        return subs_list

    def run_translate(self, definition):
        """Execute translations as defined"""
        my_srt = srt()
        my_tr = translateLocally() # preconfigured with binary and model
        res = 0
        sub_len = len(definition['files'])
        for cpt in range(0, sub_len):
            left = pathjoin(definition['in_dir'], definition['files'][cpt])
            right = pathjoin(definition['out_dir'], definition['files'][cpt][:-3]+'fr.srt')
            left_conv = left[:-3] + "en.txt"
            if sub_len == 1 and 'unique_srt_out' in definition:
                right_conv = definition['unique_srt_out']
            else:
                right_conv = left[:-3] + "fr.txt"
            my_srt.srt_to_txt(left, left_conv)
            my_tr.translate(left_conv, right_conv)
            my_srt.txt_to_srt(right_conv, right)
        return res
