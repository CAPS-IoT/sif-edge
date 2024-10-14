from abc import ABC
from pprint import pprint
from typing import List
from threading import Thread, Lock
from multiprocessing import Queue

import os
import pickle
import common
import traceback


class Scheduler(ABC):
    def __init__(self, dispatcher: "Queue[common.Invocation]",
                 base_path: str = "/data", chk_name: str = "scheduler.pkl"):
        super(Scheduler, self).__init__()
        self.chk_name = chk_name
        self.base_path = base_path
        self.function_loop: List[common.Function] = []
        self.event_loop: Queue[common.Event] = Queue()
        self.dispatcher: Queue[common.Invocation] = dispatcher
        self.restore_chk(os.path.join(base_path, chk_name))
        self.lock = Lock()

    def return_event_loop(self) -> Queue:
        return self.event_loop

    def register_fn(self, fn: common.Function):
        self.lock.acquire(blocking=True)
        self.function_loop.append(fn)
        path = os.path.join(self.base_path, self.chk_name)
        self.handle_chk(path)
        self.lock.release()

    def restore_chk(self, path: str):
        if os.path.isfile(path):
            with open(path, "rb") as chk:
                self.function_loop = pickle.load(chk)
            print("The following functions have been restored:")
            for fn in self.function_loop:
                print(fn.print())

    def generate_invocation(self, fn: common.Function):
        path = os.path.join(self.base_path, self.chk_name)
        # self.function_loop.remove(fn)
        self.handle_chk(path)
        inv = fn.generate_invocation()
        self.dispatcher.put(inv, True)

    def handle_chk(self, path: str):
        with open(path, "wb") as chk:
            pickle.dump(self.function_loop, chk)

    def submit_event(self):
        pass

    def wait_loop(self) -> Thread:
        scheduler_thr = Thread(target=self._wait_loop)
        scheduler_thr.start()
        return scheduler_thr

    def _wait_loop(self):
        while True:
            event = self.event_loop.get(True)
            self.lock.acquire(blocking=True)
            for fn in self.function_loop:
                try:
                    print("---- FUNCTIONS ----")
                    ready_inv = fn.update_event(event)
                    pprint(fn, depth=10, indent=6, compact=True)
                    print(f"//// FUNCTIONS-{ready_inv} ////")
                    if ready_inv:
                        self.generate_invocation(fn)
                    pprint(fn, depth=10, indent=6, compact=True)
                    print("++++ FUNCTIONS ++++")
                except Exception as errf:
                    print(f"Error during generating invocations {errf}")
                    traceback.print_exc()
                finally:
                    print(("\n\n"))
            self.lock.release()
