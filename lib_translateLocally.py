from os.path import isfile
from os import system

# All right
TR_OK = 0
# Can't open filename transmitteed
TR_INVALID_FILE = 1
# Source/Target languages unsupported by target libretranslate instance
TR_LANG_MIX_UNSUPPORTED = 2

class translateLocally:
    """A class to use translateLocally HTML english to french tiny
    """
    def __init__(self):
        # Parameters
        self._parameters = {
            "executable": "/usr/bin/translateLocally",
            "model": "-m en-fr-tiny",
            "format": "--html"
        }

    def setFormat(self, mode:str):
        """Set if file is txt or HTML"""
        if mode == "txt":
            self._parameters['format'] = ""
        elif mode == "html":
            self._parameters['format'] = "--html"
        return TR_OK

    def translate(self, file_in:str, file_out:str):
        """Translate HTML files, EN to FR"""
        if not isfile(file_in):
            return TR_INVALID_FILE
        cmd = f"{self._parameters['executable']} "
        cmd += f"{self._parameters['model']} {self._parameters['format']} "
        cmd += f'--input "{file_in}" --output "{file_out}"'
        print("RUN:",cmd)
        system(cmd)
        return TR_OK
