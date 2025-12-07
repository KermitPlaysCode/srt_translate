"""LIbrary to simplify my usage of translation : LibreTranslate"""

from os.path import isfile
import requests

# Request timeout as seconds
HTTP_REQUEST_TIMEOUT = 3600

# All right
TR_OK = 0
# Can't open filename transmitteed
TR_INVALID_FILE = 1
# Source/Target languages unsupported by target libretranslate instance
TR_LANG_MIX_UNSUPPORTED = 2
# Can't download reponse translated file
TR_ERR_DL_TRANSLATED = 3
TR_NO_REQUEST_SENT = 4

class TranslateLibreTranslate:
    """A class to use LibreTranslate english to french
    """
    def __init__(self, uri:str):
        """Constrcutor sets the LibreTranslate URI"""
        self._query = {}
        self._response = None
        self._fin = None
        self._err_msg = ""
        uri_path = "translate"
        if uri[:-1] == '/':
            uri += uri_path
        else:
            uri += '/' + uri_path
        self._parameters = {
            "uri": uri,
            "lang_src": "en",
            "lang_dst": "fr",
            "content_type": 'application/json; charset=utf8'
        }

    def _build_query(self, file_in:str):
        """Create data parameters for a translation query"""
        self._fin = open(file_in, 'r', encoding='utf-8')
        to_translate = ""
        with open(file_in, "r", encoding='utf-8') as fin:
            to_translate = fin.read()
        self._query = {
            'q': to_translate,
            'source': self._parameters['lang_src'],
            'target': self._parameters['lang_dst'],
            'format': 'text'
        }
        return TR_OK

    def _send_query(self):
        """Sends a translation query and get the response"""
        self._response = requests.post(
            self._parameters['uri'],
            json=self._query,
            timeout=HTTP_REQUEST_TIMEOUT
            )
        return TR_OK

    def _work_response(self, file_out:str):
        ret_code = TR_OK
        if self._response is None:
            return TR_NO_REQUEST_SENT
        if self._response.status_code == 200:
            dl_uri = self._response.json()['translatedFileUrl']
            translated = requests.get(
                dl_uri,
                timeout=HTTP_REQUEST_TIMEOUT
                )
            if translated.status_code == 200:
                with open(file_out, "w", encoding='utf-8') as fout:
                    fout.write(translated.content.decode('utf-8'))
            else:
                ret_code = TR_ERR_DL_TRANSLATED
        else:
            self._err_msg = self._response.json()['error']
            ret_code = self._response.status_code
        return ret_code

    def translate(self, file_in:str, file_out:str):
        """Translate file, EN to FR"""
        ret_code = TR_OK
        if not isfile(file_in):
            return TR_INVALID_FILE
        ret_code = self._build_query(file_in)
        if ret_code != TR_OK:
            return ret_code
        ret_code = self._send_query()
        if ret_code != TR_OK:
            return ret_code
        ret_code = self._work_response(file_out)
        return ret_code

    def get_err_msg(self):
        """Retrurns last error message"""
        return self._err_msg
