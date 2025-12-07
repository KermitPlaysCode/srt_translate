"""LIbrary to simplify my usage of translation : Argos"""

from os.path import isfile, abspath
from os import environ, remove as file_remove

import argostranslate.package
import argostranslate.translate
from argostranslatefiles import argostranslatefiles

# All right
TR_OK = 0
# Can't open filename transmitteed
TR_INVALID_FILE = 1
# Source/Target languages unsupported by target libretranslate instance
TR_LANG_MIX_UNSUPPORTED = 2
TR_ERR_TRANSLATION_ENGINE = 3

class TranslateArgos:
    """A class to use argos to translate en to fr
    """
    def __init__(self, cuda=False):
        # Parameters
        self._parameters = {
            "lang_src": "en",
            "lang_dst": "fr",
            "format": ""
        }
        if cuda:
            environ['ARGOS_DEVICE_TYPE']='cuda'
        self._prepared = False
        self._translation = None


    def _dl_languages(self) -> None:
        """Argos downloads needed package"""
        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        available_package = list(
            filter(
                lambda x: x.from_code == self._parameters['lang_src'] and \
                    x.to_code == self._parameters['lang_dst'], available_packages
            )
        )[0]
        download_path = available_package.download()
        argostranslate.package.install_from_path(download_path)
        return

    def _prep_engine(self):
        """Setup translation model ready for execution"""
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = list(filter(
                lambda x: x.code == self._parameters['lang_src'],
                installed_languages))[0]
        to_lang = list(filter(
                lambda x: x.code == self._parameters['lang_dst'],
                installed_languages))[0]
        self._translation = from_lang.get_translation(to_lang)
        return

    def _lang_init(self):
        """Initialize stuff to prepare Argos translation"""
        self._dl_languages()
        self._prep_engine()
        self._prepared = True

    def translate_text(self, text:str) -> str:
        """Translate text content"""
        res = ""
        if not self._prepared:
            self._lang_init()
        if self._translation is not None:
            res = self._translation.translate(text)
        return res

    def translate(self, file_in:str="", file_out:str=""):
        """Translate a file"""
        if not self._prepared:
            self._lang_init()
        if not isfile(file_in):
            return TR_INVALID_FILE
        if self._translation is None:
            return TR_ERR_TRANSLATION_ENGINE
        translated_file = argostranslatefiles.translate_file(self._translation, abspath(file_in))
        if translated_file:
            data = None
            with open(translated_file, "r", encoding='ansi') as fin:
                data = fin.read()
            with open(file_out, "w", encoding='utf-8') as fout:
                fout.write(data)
            file_remove(translated_file)
        return TR_OK
