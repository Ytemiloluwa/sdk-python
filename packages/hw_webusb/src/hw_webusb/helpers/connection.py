import usb.core
import usb.util
from interfaces import DeviceConnectionError, DeviceConnectionErrorType
from ..logger import logger

supported_devices = [{"vendorId": 0x3503, "productId": 259}]


async def create_port() -> usb.core.Device:
    try:
        devices = []
        for device_filter in supported_devices:
            found_devices = list(
                usb.core.find(
                    idVendor=device_filter["vendorId"],
                    idProduct=device_filter["productId"],
                    find_all=True,
                )
            )
            devices.extend(found_devices)

        if not devices:
            logger.error("No supported WebUSB devices found")
            raise DeviceConnectionError(DeviceConnectionErrorType.NOT_CONNECTED)

        # Return the first matching device
        logger.debug(f"Found {len(devices)} supported WebUSB devices")
        return devices[0]
    except usb.core.USBError as e:
        logger.error(f"USB error when finding device: {e}")
        raise DeviceConnectionError(DeviceConnectionErrorType.NOT_CONNECTED)
    except Exception as e:
        logger.error(f"Unexpected error when finding device: {e}")
        raise DeviceConnectionError(DeviceConnectionErrorType.NOT_CONNECTED)
