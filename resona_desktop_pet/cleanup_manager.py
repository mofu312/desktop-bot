import atexit
import signal
import sys
import logging
import psutil
import subprocess
from typing import Callable, List, Set
logging.basicConfig(format='[%(asctime)s] [Cleanup] %(message)s', level=logging.INFO)
class CleanupManager:
    _instance = None
    _cleanup_callbacks: List[Callable] = []
    _registered_pids: Set[int] = set()
    _is_cleaning_up = False
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CleanupManager()
        return cls._instance
    def __init__(self):
        if CleanupManager._instance is not None:
            raise Exception("This class is a singleton!")
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        atexit.register(self.cleanup)
    def register(self, callback: Callable):
        if callback not in self._cleanup_callbacks:
            self._cleanup_callbacks.append(callback)
    def register_pid(self, pid: int):
        self._registered_pids.add(pid)
    def unregister(self, callback: Callable):
        if callback in self._cleanup_callbacks:
            self._cleanup_callbacks.remove(callback)
    def _handle_signal(self, signum, frame):
        logging.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)
    def cleanup(self):
        if self._is_cleaning_up:
            return
        self._is_cleaning_up = True
        logging.info("Starting cleanup...")
        for callback in reversed(self._cleanup_callbacks):
            try:
                callback()
            except Exception as e:
                logging.error(f"Error during cleanup callback: {e}")
        for pid in list(self._registered_pids):
            try:
                logging.info(f"Killing process {pid}...")
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], 
                                   capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                parent.terminate()
                _, alive = psutil.wait_procs(children + [parent], timeout=3)
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                logging.error(f"Error killing process {pid}: {e}")
        logging.info("Cleanup complete.")
cleanup_manager = CleanupManager.get_instance()
def register_cleanup(callback: Callable):
    cleanup_manager.register(callback)
def register_pid(pid: int):
    cleanup_manager.register_pid(pid)
