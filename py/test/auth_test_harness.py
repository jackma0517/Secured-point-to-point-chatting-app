import sys
import queue
import threading

sys.path.append('..')
from authenticate import Authentication
from config import Mode


def queue_shift(input_queue, output_queue):
    """
    Mimics the socket connection between two instances
    """
    while True:
        if not input_queue.empty():
            output_queue.put(input_queue.get())


def main():
    c_send_q = queue.Queue()
    c_recv_q = queue.Queue()
    s_send_q = queue.Queue()
    s_recv_q = queue.Queue()

    threading.Thread(target=queue_shift, args=(c_send_q, s_recv_q)).start()
    threading.Thread(target=queue_shift, args=(s_send_q, c_recv_q)).start()

    skrt_key = 'abc'
    c_dh = None
    s_dh = None
    c_auth_err = False
    s_auth_err = False

    c_auth = Authentication()
    s_auth = Authentication()

    threading.Thread(target=c_auth.authenticate, args=(skrt_key, c_recv_q, c_send_q, Mode.CLIENT, c_dh, c_auth_err)).start()
    threading.Thread(target=s_auth.authenticate, args=(skrt_key, s_recv_q, s_send_q, Mode.SERVER, c_dh, c_auth_err)).start()


if __name__ == '__main__':
    main()