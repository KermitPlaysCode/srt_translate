"""Module to run ffmpeg and extract subs"""

import os
from pymediainfo import MediaInfo
from config import extract_audio_lang

# My error codes


class FfmpegExtractSubs:
    """Class to run ffmpeg and extract subs. Relies on mediainfo to gather details"""
    E_NO_ERROR = 0
    E_MISSING_FFMPEG = -1
    E_MISSING_PARAMETER = -2
    E_MISSING_SUBS = -3
    E_NO_STREAM_FOUND = -4
    E_INPUT_FILE_OPEN_ERROR = -5

    def __init__(self, ffmpeg):
        """Constructor
        Parameters
        ----------
        - ffmpeg : path to ffmpeg executable
        """
        if os.path.isfile(ffmpeg):
            self.__ffmpeg = ffmpeg
        else:
            self.__ffmpeg = None
        self.mi = None
        self.encoding = "utf-8"

    def extract(self, source, destination, test=False, lang=extract_audio_lang):
        """Finds subs and translate, preferrably with lang
        File will be placed in the same directory (ready to use)

        Parameters
        ----------
        - source : video file
        - destination : translated subs file
        """
        if not self.__test_ffmpeg():
            return self.E_MISSING_FFMPEG
        if not destination.endswith(".srt"):
            destination += ".srt"
        with open(source, "rb") as fin:
            self.mi = MediaInfo.parse(fin)
        # Open did not work, self.mi still None
        if self.mi is None:
            return self.E_INPUT_FILE_OPEN_ERROR
        # Autofind the track
        stream_id = self.__determine_track(auto_first=lang)
        if stream_id < 0:
            return self.E_NO_STREAM_FOUND
        cmd = f"{self.__ffmpeg} -y -loglevel error -i \"{source}\" -map 0:"
        cmd += f"{stream_id} -vn -an -c:s srt \"{destination}\""
        if test:
            print(cmd)
        else:
            os.system(cmd)
        return self.E_NO_ERROR

    def __test_ffmpeg(self):
        """Check ffmpeg presence"""
        if os.path.isfile(self.__ffmpeg):
            return True
        return False

    def __determine_track(self, auto_first=''):
        """Look for a track to extract, preferrably with langguage passed as 'auto_first'
            - if only 1 track: get this one
            - if multiple tracks:
                - if one has lang 'auto_first' => take it (if multiple, only first found is considered)
                - else tkae first one
        
        Parameters
        ----------
        - auto_first: optionnal; if set, takes the first track with specified language, like 'en'
        
        Returns:
        str: id of the track for ffmpeg
        """
        if len(self.mi.text_tracks) == 0:
            # No subs
            return -1
        elif len(self.mi.text_tracks) == 1:
             # Exactly one sub
            r = self.__get_track_streamid(self.mi.text_tracks[0])
            return r
        else:
            # More than 1 track => default : take first sub track
            r = self.__get_track_streamid(self.mi.text_tracks[0])
            # Look for the first track with requested language
            for tr in self.mi.text_tracks:
                if tr.language == auto_first:
                    r = self.__get_track_streamid(tr)
        return r

    def __get_track_streamid(self, track):
        """Return ID of the stream (might not match the index of the table)

        Parameters
        ----------
        - track: the track entry

        Returns:
        int: stream ID
        """
        return int(track.streamorder)
