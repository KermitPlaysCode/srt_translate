"""Simple timer"""

import time

E_OK = 0
E_START_FIRST = 1
E_ALREADY_STARTED = 2

class chrono:
    """Measure time between start and stop"""
    def __init__(self):
        """Constructor"""
        self._tstart = 0
        self._tend = 0
        self._flag_s = False
        self._flag_e = False
        self._delay = 0

    def start(self) -> None:
        """Set beginning of measure"""
        ret = E_OK
        if not self._flag_s:
            self._tstart = time.time()
            self._flag_s = True
            self._flag_e = False
        else:
            ret = E_ALREADY_STARTED
        return ret

    def stop(self) -> None:
        """Set end of measure"""
        ret = E_OK
        if self._flag_s:
            self._tend = time.time()
            self._flag_e = True
            self._delay = self._tend - self._tstart
        else:
            ret = E_START_FIRST
        return ret

    def get_time(self) -> float:
        """return the last measure - 0 if none"""
        return self._delay

if __name__ == "__main__":
    c = chrono()
    c.start()
    for x in range(50000000):
        y = x ** .35
    c.stop()
    print(c.get_time())
