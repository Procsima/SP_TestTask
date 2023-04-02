import threading


class MsgQueue:
    def __init__(self):
        self.data = []
        self.semaphore = threading.Semaphore(1)

    def put(self, item):
        with self.semaphore:
            self.data.append(item)

    def get(self):
        item = ''
        with self.semaphore:
            item = self.data[0]
            self.data = self.data[1:]
        return item

    def empty(self) -> bool:
        return len(self.data) == 0
