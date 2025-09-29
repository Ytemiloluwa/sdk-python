import uuid
import threading
from typing import List, Optional, Dict, Any
import serial
from packages.interfaces.connection import PoolData

class DataListener:
    """
    Listens for data events from a serial port connection and manages a data pool.
    """
    def __init__(self, params: Dict[str, Any]):
        self.connection = params.get("connection")
        self.on_close_callback = params.get("onClose")
        self.on_error_callback = params.get("onError")
        self.listening = False
        self.pool: List[PoolData] = []
        self.pool_lock = threading.Lock()
        self.read_thread = None
        self.start_listening()

    def destroy(self) -> None:
        self.stop_listening()

    def is_listening(self) -> bool:
        return self.listening

    async def receive(self) -> Optional[bytearray]:
        """
        Get and remove the first data item from the pool.
        """
        with self.pool_lock:
            if not self.pool:
                return None
            return self.pool.pop(0).get("data")

    def peek(self) -> List[PoolData]:
        """
        Get a copy of all data items in the pool without removing them.
        """
        with self.pool_lock:
            return self.pool.copy()

    def start_listening(self) -> None:
        if self.listening:
            return

        self.listening = True
        self.read_thread = threading.Thread(target=self._read_loop)
        self.read_thread.daemon = True
        self.read_thread.start()

    def stop_listening(self) -> None:
        self.listening = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)

    def _read_loop(self) -> None:
        """Background thread that reads data from the serial port."""
        try:
            while self.listening and self.connection and self.connection.is_open:
                try:
                    # Check if data is available
                    if self.connection.in_waiting > 0:
                        # Read available data
                        data = self.connection.read(self.connection.in_waiting)
                        if data:
                            self._on_data(data)
                    # Small sleep to prevent CPU hogging
                    threading.Event().wait(0.01)
                except serial.SerialException as e:
                    if self.on_error_callback:
                        self.on_error_callback(e)
                    break
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(e)
        finally:
            if self.on_close_callback:
                self.on_close_callback()

    def _on_data(self, data: bytes) -> None:
        """
        Handle incoming data.
        """
        with self.pool_lock:
            self.pool.append({
                "id": str(uuid.uuid4()),
                "data": bytearray(data)
            })

    def _on_close(self) -> None:
        if self.on_close_callback:
            self.on_close_callback()

    def _on_serial_port_error(self, error: Exception) -> None:
        """
        Handle serial port errors.
        """
        if self.on_error_callback:
            self.on_error_callback(error)
