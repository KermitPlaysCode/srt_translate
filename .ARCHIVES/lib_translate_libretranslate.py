from os.path import isfile
import urllib3
import json

# All right
tr_OK = 0
# Can't open filename transmitteed
tr_INVALID_FILE = 1
# Source/Target languages unsupported by target libretranslate instance
tr_LANG_MIX_UNSUPPORTED = 2

class translateLibreTranslate:
    """A simple class to automatically read a text file,
    Apply updates that apparently improve translation (empirically discovered)
    """
    def __init__(self):
        # Parameters to translate
        self.__parameters = {
            'query_file': "",
            'query_language': "en",
            'response_file': "",
            'response_language': "fr",
            'format': "html"
        }
        # URL to libretranslate API
        self.__url = None
        self.__supported_lang = None
        # URLlib handler
        self.__http = urllib3.PoolManager()

    def set_libretranslate(self, lt_host='127.0.0.1', lt_port='5000', lt_proto='http'):
        """
        Create URL to libretranslate API, from parameters
        Get supported languages
        """
        # Build URL from parameters
        self.__url = f"{lt_proto}://{lt_host}:{lt_port}/"
        # Retrieve supported language
        resp = self.__http.request("GET", self.__url + 'languages')
        self.__supported_lang = json.loads(resp.data.decode())
        return tr_OK

    def set_input(self, fname, lang):
        """
        Set input file and language
        """
        res = tr_INVALID_FILE
        if os.path.isfile(fname):
            self.__query_file = fname
            self.__query_language = lang
            res = tr_OK
        return res

    def set_output(self, fname, lang):
        """
        Set output file and language
        """
        res = tr_INVALID_FILE
        if os.path.isfile(fname):
            self.__response_file = fname
            self.__response_language = lang
            res = tr_OK
        return res

    def __check_lang(self, lang_from, lang_to):
        """
        print(self.__supported_lang)
        [{'code': 'en', 'name': 'English', 'targets': ['en', 'fr']}, {'code': 'fr', 'name': 'French', 'targets': ['en', 'fr']}]
        """
        for lang in self.__supported_lang:
            if lang['code'] == lang_from:
                return tr_OK
        return tr_OK

    def translate_html(self, content, lang_from='en', lang_to='fr'):
        """
        Translate a simple string 'content'
        English to french by default
        Parameters:
          - content: string to translate
          - lang_from: content language
          - lang_to: target language
        """
        # Check kanguage couple is support
        if self.__check_lang(lang_from, lang_to) != tr_OK:
            return tr_LANG_MIX_UNSUPPORTED
        # Sending a request and getting back response as HTTPResponse object.
        resp = self.__http.request(
            "POST",
            self.__url + '/translate',
            fields={
                "q": content,
                "source": lang_from,
                "target": lang_to,
                "format": 'html' # 'html' or 'text'
            }
        )
        self.translated_html = json.loads(resp.data.decode())['translatedText']
        return self.translated_html

