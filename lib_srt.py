"""SRT reference @ https://docs.fileformat.com/video/srt/"""

import re

BLK_ID = 1
BLK_TIMES = 2
BLK_TEXT = 4
BLK_BLANK = 8
BLK_MISPLACED_BLANK = 16
# blk = [BLK_ID, BLK_TIMES, BLK_TEXT, BLK_BLANK]

BALISE = 'div'
NEWLINE = '\n'

char_matrix = {
    '-': 'dash',
    '*': 'star'
}

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

    # 4 _is_valid_xxx() = 4 types of blocks in SRT file
    # And
    #  ID
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

    def _check_encoding(self, f:str):
        """Check encoding : is it utf8 ?
        https://stackoverflow.com/questions/436220/how-to-determine-the-encoding-of-text
        """
        encodings = ['utf-8', 'windows-1250', 'windows-1252']
        for enc in encodings:
            try:
                fh = open(f, 'r', encoding=enc)
                fh.readlines()
                fh.close()
            except UnicodeDecodeError:
                pass
            else:
                break
        return enc # pyright: ignore[reportPossiblyUnboundVariable]

    # A separator line (leads to current ID to increment)
    def _is_valid_blank(self, txt):
        """Check timestamps format"""
        if txt == "":
            return True
        return False
    
    # loop and save v2
    def _detect_and_save_line(self, line:str):
        """Analyze a line of content and store in a table"""
        if self._is_valid_id(line):
            self._current_sub['id'] = line
            return BLK_ID
        elif self._is_valid_times(line):
            self._current_sub['times'] = line
            return BLK_TIMES
        elif self._is_valid_blank(line):
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

    def _load(self, input_srt:str):
        """Load srt file, read lines to initiate analysis of the content"""
        self._current_sub = {}
        self._current_id = 1
        self._current_line = 0
        with open(input_srt, "r", encoding='utf-8') as fin:
            line = fin.readline()
            while line != "":
                line_ascii = line.rstrip().encode('ascii', 'ignore').decode('ascii')
                self._current_line += 1
                self._detect_and_save_line(line_ascii)
                line = fin.readline()
        print(f'_load: lines={self._current_line} id={self._current_id}')
        return 0

    def srt_to_txt(self, input_srt, output_txt):
        """Convert SRT into a text file + a separate file with ID and timecodes
        txt_content = text strings only, 1 sub per line"""
        print(f"SRT conversion '{input_srt}' > '{output_txt}'")
        r = 0
        txt_content = ""
        self.subs = []
        r = self._load(input_srt)
        if r != 0 or not self.subs:
            txt_content += f"Error {r} and count subs={len(self.subs)}{NEWLINE}"
            return 0
        for sub in self.subs:
            txt_content += ' '.join(sub['text']) + NEWLINE
        with open(output_txt, "w", encoding="utf-8") as fout:
            fout.write(txt_content)
        return len(txt_content)

    def txt_to_srt(self, input_txt, output_srt):
        """Convert translated TXT back to SRT using saved id and timecodes"""
        print(f"TXT conversion '{input_txt}' > '{output_srt}'")
        srt_content = ""
        txt_line = 0
        with open(input_txt, "r", encoding="utf-8") as fin:
            for sub in self.subs:
                translated = fin.readline()
                txt_line += 1
                if int(sub['id']) == txt_line:
                    srt_content += f"{sub['id']}{NEWLINE}"
                    srt_content += f"{sub['times']}{NEWLINE}"
                    srt_content += f"{translated}{NEWLINE}"
                else:
                    print(f"Err: txt_line={txt_line} id={sub['id']} tc={sub['times']} {translated}")
        with open(output_srt, "w", encoding='utf-8') as fout:
            print("Save to", output_srt)
            fout.write(srt_content)
        return 0

    def all(self):
        """Sends back the bunch of subs once extracted from the SRT file"""
        return self.subs
