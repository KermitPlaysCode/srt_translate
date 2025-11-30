"""SRT reference @ https://docs.fileformat.com/video/srt/"""

import re

BLK_ID = 1
BLK_TIMES = 2
BLK_TEXT = 4
BLK_BLANK = 8
BLK_MISPLACED_BLANK = 16

class srt():
    """
    Class to manipulate subtitles from SRT file
    """

    def __init__(self):
        """Constructor"""
        self._current_block = None
        onetime = r"\d{2}:\d{2}:\d{2},\d{3}"
        self._re_times = r"^"+onetime+' --> '+onetime+"$"
        self._current_sub = {}
        self.subs = []
        self._current_id = 1
        self._current_line = 0 # keep track where is the issue, when I detect one
        return
    def _is_valid_id(self, txt:str):
        """ Check that ID is a number AND is the current ID"""
        if txt.isdigit() :
            if int(txt) == self._current_id:
                return True
        return False

    # A couple of timestamps
    def _is_valid_times(self, txt:str):
        """Check timestamps format"""
        # Loks like "00:05:16,400 --> 00:05:25,300"
        if re.search(self._re_times, txt):
            return True
        return False

    # The subtitle
    def _is_valid_text(self, txt:str):
        """Ensure we have a string - not empty"""
        if txt != "" and not self._is_valid_times(txt):
            return True
        return False

    # A separator line (leads to current ID to increment)
    """Check timestamps format"""
    def _is_valid_blank(self, txt):
        if txt == "":
            return True
        return False
    
    # loop and save v2
    def _detect_and_save_line(self, line:str):
        """Analyze a line of content and store in a table"""
        line_clean = line.rstrip()
        if self._is_valid_id(line_clean):
            self._current_sub['id'] = line_clean
            return BLK_ID
        elif self._is_valid_times(line_clean):
            self._current_sub['times'] = line
            return BLK_TIMES
        elif self._is_valid_blank(line_clean):
            t_id = 'id' in self._current_sub
            t_times = 'times' in self._current_sub
            t_text = 'text' in self._current_sub
            if t_id and t_times and t_text:
                # 3 conditions met => youpi
                self.subs.append({
                                'id': self._current_sub['id'],
                                'times': self._current_sub['times'],
                                'text': self._current_sub['text']
                            })
                self._current_id += 1
                self._current_sub = {}
                return BLK_BLANK
            else:
                print(f"Warning : blank line detected and missing data : ID={t_id} TIMES={t_times} TEXT={t_text} LINE={self._current_line}")
                # Reset anyway
                self._current_id += 1
                self._current_sub = {}
            return BLK_MISPLACED_BLANK
        elif self._is_valid_text(line):
            if 'text' not in self._current_sub:
                self._current_sub['text'] = [line]
            else:
                self._current_sub['text'].append(line)
            return BLK_TEXT
        else:
            return 64


        return