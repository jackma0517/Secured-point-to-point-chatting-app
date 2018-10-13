import datetime


class Logger(object):

    @staticmethod
    def log(msg, is_server=False):
        machine = "SERVER" if is_server else "CLIENT"
        time = datetime.datetime.now().time().strftime('%H:%M')
        info_msg = "(%s) [%s] " % (time, machine)
        info_msg += msg
        print info_msg
