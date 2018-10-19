import logging
import threading


class Token():
    def __init__(self):
        self.debug = False
        self.step_next = False
        self.wait_lock = threading.Lock()


def wait_if_debug(token):
    token.wait_lock.acquire()
    if (token.debug):
        logging.info('Press continue to step')
        while (not token.step_next and token.debug):
            continue
        token.step_next = False
    token.wait_lock.release()
    return