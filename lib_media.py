"""Module to run ffmpeg and extract subs"""

from os.path import isfile
from pymediainfo import MediaInfo

# My error codes
E_NO_ERROR = 0
E_MISSING_FFMPEG = -1
E_MISSING_PARAMETER = -2
E_MISSING_SUBS = -3

class FfmpegExtractSubs:
    """Class to run ffmpeg and extract subs"""
    def __init__(self):
        self.__ffmpeg = None
        self.__mi = None
        self.encoding = "utf-8"

    def set_ffmpeg_location(self, path_to_exec):
        """Set ffmpeg presence before saving its path"""
        if isfile(path_to_exec):
            self.__ffmpeg = path_to_exec
            return True
        return False        
    
    def extract_sub(self, source, destination, test=False):
        """Finds english subs and translate
        File will be placed in the same directory (ready to use)

        Parameters
        ----------
        - source : video file
        - destination : subs file, SRT format (auto-append .srt if not present)
        - test : True=>only prints the ffmpeg command; default to False
        """
        if self.__ffmpeg is None:
            return E_MISSING_FFMPEG
        if destination[-4:] != ".srt":
            destination += ".srt"
        with open(source, "rb") as fin:
            self.__mi = MediaInfo.parse(fin)
        stream_id = self.__determine_track(auto_first='en')
        cmd = f"{self.__ffmpeg} -y -loglevel error -i \"{source}\" -map 0:"
        cmd += f"{stream_id} -vn -an -c:s srt \"{destination}\""
        if test:
            print(cmd)
        else:
            os.system(cmd)
        return E_NO_ERROR

    def __determine_track(self, auto_first=''):
        """Look for tracks; if many are available, ask user
        
        Parameters
        ----------
        - auto_first: optionnal; if set, takes the first track with specified language, like 'en'
        
        Returns:
        str: id of the track for ffmpeg
        """
        self.list_track_subs = self.__mi.text_tracks
        if len(self.list_track_subs) == 0:
            r = -1
        elif len(self.list_track_subs) == 1:
            r = self.__validate_track(self.list_track_subs[0])
        else:
            if auto_first == '':
                r = self.__select_manual()
            else:
                r = self.__select_auto(auto_first=auto_first)
        return r

    def __select_auto(self, auto_first=''):
        """Choose the track automatically: must be text, must be utf-8, must be language set"""
        for tr in self.list_track_subs:
            r = self.__validate_track(tr)
            if r >= 0:
                return r
        return r

    def __select_manual(self):
        """Choose the track manually: user has to make the choice"""
        track_to_stream = {}
        print("Choose wisely :")
        for tr in self.list_track_subs:
            print(f"[{tr.track_id}] (Stream {tr.streamorder}) in {tr.language}, format {tr.format} ")
            track_to_stream[str(tr.track_id)] = tr.streamorder
        print(" Your choice ? ", end = '')
        choice = input()
        assert choice in track_to_stream.keys()
        return track_to_stream[choice]

    def __validate_track(self, track):
        lang = track.languauge
        form = track.format
        "TEXT".lower()
        if lang == 'en' and form.mi.lower() == 'utf-8':
            return track.streamorder
        return -1
