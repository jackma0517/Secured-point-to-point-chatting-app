import logging


class Token():
    def __init__(self):
        self.debug = False
        self.step_next = False


def wait_if_debug(token):
    if (token.debug):
        logging.info('Press continue to step')
        while (not token.step_next and token.debug):
            continue
        token.step_next = False
    return