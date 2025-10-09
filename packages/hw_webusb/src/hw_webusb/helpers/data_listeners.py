import asyncio
import uuid
from typing import Any, Dict, List, Optional

import usb.core
import usb.util

from interfaces import (
    DeviceConnectionError,
    DeviceConnectionErrorType,
    PoolData,
)

from ..logger import logger


class DataListener:
    def __init__(self, params: Dict[str, Any]):
        self.connection: usb.core.Device = params["connection"]
        self.interface_number: int = params["interface_number"]
        self.endpoint_in: int = params["endpoint_in"]
        self.endpoint_out: int = params["endpoint_out"]
        self.listening: bool = True
        self.pool: List[PoolData] = []

    @staticmethod
    async def create(connection: usb.core.Device) -> "DataListener":
        interface_number = 0
        endpoint_in = 0
        endpoint_out = 0

        try:
            if connection.is_kernel_driver_active(0):
                connection.detach_kernel_driver(0)

            # Get configuration
            cfg = connection.get_active_configuration()
            if not cfg:
                connection.set_configuration()
                cfg = connection.get_active_configuration()

            if not cfg:
                raise DeviceConnectionError(DeviceConnectionErrorType.FAILED_TO_CONNECT)

            for interface in cfg:
                for setting in interface:
                    if setting.bInterfaceClass == 0xFF:
                        interface_number = interface.bInterfaceNumber
                        for endpoint in setting:
                            if (
                                usb.util.endpoint_direction(endpoint.bEndpointAddress)
                                == usb.util.ENDPOINT_OUT
                            ):
                                endpoint_out = endpoint.bEndpointAddress
                            elif (
                                usb.util.endpoint_direction(endpoint.bEndpointAddress)
                                == usb.util.ENDPOINT_IN
                            ):
                                endpoint_in = endpoint.bEndpointAddress

            # Claim interface
            usb.util.claim_interface(connection, interface_number)

            # Set alternate setting
            connection.set_interface_altsetting(interface_number, 0)

            connection.ctrl_transfer(
                bmRequestType=0x21, bRequest=0x22, wValue=0x01, wIndex=interface_number
            )

            return DataListener(
                {
                    "connection": connection,
                    "interface_number": interface_number,
                    "endpoint_in": endpoint_in,
                    "endpoint_out": endpoint_out,
                }
            )

        except usb.core.USBError as e:
            logger.error(f"USB error during device setup: {e}")
            raise DeviceConnectionError(DeviceConnectionErrorType.FAILED_TO_CONNECT)
        except Exception as e:
            logger.error(f"Unexpected error during device setup: {e}")
            raise DeviceConnectionError(DeviceConnectionErrorType.FAILED_TO_CONNECT)

    def is_listening(self) -> bool:
        return self.listening

    async def receive(self) -> Optional[bytearray]:
        if self.pool:
            return self.pool.pop(0).get("data")
        return await self.receive_new()

    async def send(self, data: bytearray) -> None:
        try:
            # Use asyncio.to_thread to prevent blocking
            await asyncio.to_thread(
                self.connection.write, self.endpoint_out, data, timeout=1000
            )
        except usb.core.USBError as e:
            logger.error(f"USB error during write: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during write: {e}")

    async def peek(self) -> List[PoolData]:
        new_data = await self.receive_new()
        if new_data:
            self.pool.append({"id": str(uuid.uuid4()), "data": new_data})
        return self.pool.copy()

    async def receive_new(self) -> Optional[bytearray]:
        try:
            # Use asyncio.to_thread to prevent blocking
            result = await asyncio.to_thread(
                self._read_usb_data, self.endpoint_in, 6 * 1024, timeout=1000
            )

            if not result or len(result) == 0:
                return None

            return bytearray(result)
        except usb.core.USBError as e:
            if e.errno == 110:
                return None
            logger.error(f"USB error during read: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during read: {e}")
            return None

    def _read_usb_data(self, endpoint: int, size: int, timeout: int = 1000) -> bytes:
        # Synchronous USB read operation to be wrapped with asyncio.to_thread
        try:
            return self.connection.read(endpoint, size, timeout)
        except usb.core.USBError as e:
            if e.errno == 110:
                return b""
            raise
