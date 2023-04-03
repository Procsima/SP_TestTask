import threading


class MsgQueue:
    def __init__(self):
        self.data = []
        self.semaphore = threading.Semaphore(1)

    def put(self, item: str) -> None:
        with self.semaphore:
            self.data.append(item)

    def get(self) -> str:
        item = ''
        with self.semaphore:
            item = self.data[0]
            self.data = self.data[1:]
        return item

    def empty(self) -> bool:
        return len(self.data) == 0


class PriorMsgQueue:
    def __init__(self):
        self.data = []
        self.semaphore = threading.Semaphore(1)

    def put(self, item: str, prior: int) -> None:
        with self.semaphore:
            self.data.append((item, prior))
            self.data.sort(key=lambda i: i[1], reverse=True)

    def get(self) -> str:
        item = ''
        with self.semaphore:
            item = self.data[0]
            self.data = self.data[1:]
        return item[0]

    def empty(self) -> bool:
        return len(self.data) == 0
