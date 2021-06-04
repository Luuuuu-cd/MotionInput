import threading

class MultiThreading:
    def check_status(self, *args):
        mode = args[-1]
        thread_1 = threading.Timer(0.1, self.check_status, args)
        thread_1.daemon = True
        thread_1.start()
        thread_2 = threading.Thread(target=mode.move_player())
        thread_2.daemon = True
        thread_2.start()

        if len(args) == 3:
            thread_3 = threading.Thread(target=mode.move_mouse())
            thread_3.daemon = True
            thread_3.start()