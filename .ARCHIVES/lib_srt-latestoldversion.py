import re
from html.parser import HTMLParser

"""SRT reference @ https://docs.fileformat.com/video/srt/"""

BLK_ID = 1
BLK_TIMES = 2
BLK_TEXT = 4
BLK_BLANK = 8
BLK_MISPLACED_BLANK = 16
blk = [BLK_ID, BLK_TIMES, BLK_TEXT, BLK_BLANK]

balise = 'p'

char_matrix = {
    '-': 'dash',
    '*': 'star'
}

class MyHTMLParser(HTMLParser):
    """
    Class to read translated HTML and process it accordingly
    """
    def _to_dict(self, array_array):
        res = {}
        for (k,v) in array_array:
            res[k] = v
        return res

    def handle_starttag(self, tag, attrs):
        if tag == balise:
            attributes = self._to_dict(attrs)
            if 'id' in attributes:
                if int(self._id) > 0:
                    self._output.append([self._id, self._text, self._nb_lines])
                    self._id = 0
                    self._text = ""
                    self._nb_lines = 0                    
                self._id = attributes['id']
        elif tag == "ul":
            pass
        elif tag == 'br':
            self._nb_lines += 1
            self._text += "\n"
        elif tag == 'i':
            self._text += "<i>"
        elif tag in self._name_matrix:
                char=self._name_matrix[tag]
                self._text += char

    def handle_endtag(self, tag):
        if tag == "li":
            self._text += "\n"
        elif tag == 'i':
            self._text += "</i>"

    def handle_data(self, data):
        self._text += data
        self._nb_lines += 1

    def init(self):
        self._id = 0
        self._text = ""
        self._output = []
        self._nb_lines = 0
        self._name_matrix = {}
        for (char,name) in char_matrix.items():
            self._name_matrix[name] = char

    def retrieve_subs(self):
        return self._output

class srt():
    """
    Class to manipulate subtitles from SRT file
    """

    def __init__(self):
        self._current_block = None
        self._srt_sub = {
            'id' : 1,
            'times' : '',
            'text' : '',
            'lines': 0
        }
        self._block_test = 0 # 4 blocks, includes blank separator => 3 blocks to test, 3 bits to set to 1
        self._next_block = BLK_ID # index in blk table
        self._current_id = 1
        self._filename = ""
        onetime = r"\d{2}:\d{2}:\d{2},\d{3}"
        self._re_times = r"^"+onetime+' --> '+onetime+"$"
        self._current_sub = None
        self.subs = []
        self._show_next = 0
        self._show_max = 0
        self._logfile = 'output.log'
        self._logopen = False
        return

    # 4 _is_valid_xxx() = 4 types of blocks in SRT file
    # And ID
    def _is_valid_id(self, txt):
        """ Check that ID is a number AND is the current ID"""
        if txt.isdigit() and int(txt) == self._current_id:
            return True
        return False

    # A couple of timestamps
    def _is_valid_times(self, txt):
        # Loks like "00:05:16,400 --> 00:05:25,300"
        if re.search(self._re_times, txt):
            return True
        return False

    # The subtitle
    def _is_valid_text(self, txt):
        if txt != "" and not self._is_valid_times(txt):
            return True
        return False

    def _check_encoding(self, f):
        """is it utf8 ?
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
        return enc

    # A separator line (leads to current ID to increment)
    def _is_valid_blank(self, txt):
        if txt == "":
            return True
        return False
    
    # Def write to log
    def _log(self, msg):
        if self._logopen:
            self._logfh.write(msg)
    
    # loop and save v2
    def _detect_and_save_line_type(self, line):
        # line winthout \r or \n
        if self._is_valid_id(line):
            self._current_sub['id'] = line
            print("ID=",line)
            return BLK_ID
        elif self._is_valid_times(line):
            self._current_sub['times'] = line
            print("TIMES=",line)
            return BLK_TIMES
        elif self._is_valid_blank(line):
            if 'id' in self._current_sub and 'times' in self._current_sub and 'text' in self._current_sub:
                # 3 conditions met => youpi
                self.subs.append({
                                'id': self._current_sub['id'],
                                'times': self._current_sub['times'],
                                'text': self._current_sub['text']
                            })
                self._current_sub = {}
                return BLK_BLANK
            return BLK_MISPLACED_BLANK
        elif self._is_valid_text(line):
            if 'text' not in self._current_sub:
                self._current_sub['text'] = [line]
            else:
                self._current_sub['text'].append(line)
            print("TEXT=",self._current_sub['text'])
            return BLK_TEXT

    def _load(self, input_srt):
        self._current_sub = {}
        line = " "
        with open(input_srt, "r", encoding='utf-8') as fin:
            while line != '':
                line = fin.readline().rstrip()
                line_type = self._detect_and_save_line_type(line)
        return 
    
    # Loop and save
    def _load_previousversion(self, input_srt):
        with open(input_srt, "r", encoding='utf-8') as fin:
            self._show_next = 0
            self._show_max = 0
            self.subs = []
            line = fin.readline()
            self._next_block = BLK_ID
            self._current_sub = {}
            self._block_test = 0
            while line != '':
                line = line.rstrip()
                if self._next_block == BLK_ID:
                    if self._is_valid_id(line):
                        self._current_sub = self._srt_sub.copy()
                        self._current_sub['id'] = self._current_id
                        self._block_test = self._block_test | self._next_block
                        self._current_sub['lines'] = 0
                        self._next_block = BLK_TIMES
                        self._show_max += 1
                    else:
                        pass
                        # nothing if it's not an ID, wait for an ID
                elif self._next_block == BLK_TIMES:
                    if self._is_valid_times(line):
                        self._current_sub['times'] = line
                        self._current_sub['text'] += "\n<ul>"
                        self._block_test = self._block_test | self._next_block
                        self._next_block = BLK_TEXT
                    else:
                        self._next_block = BLK_ID
                        self._log(f"Missing times right after ID on id={self._current_sub['id']}")
                        # no times after ID ? back to ID and log
                elif self._next_block == BLK_TEXT:
                    if self._is_valid_text(line):
                        self._current_sub['text'] = "  <li>" + line + "</li>"
                        self._current_sub['lines'] += 1
                        self._block_test = self._block_test | self._next_block
                    elif self._is_valid_blank(line):
                        if self._block_test == (BLK_ID|BLK_TIMES|BLK_TEXT):
                            self._current_sub['text'] += "</p>\n"
                            self.subs.append({
                                'id': self._current_sub['id'],
                                'times': self._current_sub['times'],
                                'text': self._current_sub['text'],
                                'lines': self._current_sub['lines']
                            })
                            # Reset tester
                            self._block_test = 0
                            # PAss to next block
                            self._current_id = self._current_id + 1
                            self._next_block = BLK_ID
                        else:
                            self._log(f"Invalid sub ID={self._current_sub['id']}")
                            self._next_block = BLK_ID
                    else:
                        self._log(f"Invalid sub ID={self._current_sub['id']}")

                line = fin.readline()
            return 0
        return 1

    def srt_to_html(self, input_srt=None, output_html=None):
        print(f"srt to html {input_srt} > {output_html}")
        r = 0
        if input_srt != None:
            r = self._load(input_srt)
        if r != 0 or self.subs==[]:
            return f"<body><html>Error {r}</body></html>"
        html_content = '<html><body>\n<ul>\n'
        for sub in self.subs:
            # Replace characters which prevents LT to work correctly
            # PAUSED for translateLocally
            #txt = sub['text']
            #for (char,name) in char_matrix.items():
            #    txt = txt.replace(char, f'<{char_matrix[char]}/>')
            html_content += f"<{balise} id=\"{sub['id']}\" times=\"{sub['times']}\""
            html_content += f"{'<br>'.join(sub['text'])}</{balise}>"
        html_content += "\n</ul></body></html>"
        if output_html is not None:
            with open(output_html, "w", encoding="utf-8") as fout:
                fout.write(html_content)
                return ""
        return html_content

    def html_to_srt(self, input_html, output_srt=None):
        parser = MyHTMLParser()
        parser.init()
        translated = None
        with open(input_html, "r", encoding="utf-8") as fin:
            translated = fin.read()
        parser.feed(translated)
        tbl_subs = parser.retrieve_subs()
        out_srt = ""
        for sub in tbl_subs:
            (num, txt, lines) = sub
            times = self.subs[int(num)-1]['times']
            txt = txt.lstrip().rstrip() # cleanup
            out_srt += f"{num}\n{times}\n{txt}\n\n"
        if output_srt is not None:
             with open(output_srt, "w", encoding="utf-8") as fout:
                fout.write(out_srt)
                return ""
        return out_srt

    def next(self):
        if self._show_next >= self._show_max:
            return {}
        res = self.subs[self._show_next]
        self._show_next +=1
        return res

    def all(self):
        return self.subs
