import serial
import serial.tools.list_ports
from typing import Dict, List
from interfaces.connection import DeviceState, IDevice, ConnectionTypeMap

supported_versions_to_device_state: Dict[str, DeviceState] = {
    # Bootloader
    "01": DeviceState.BOOTLOADER,
    # Initial
    "02": DeviceState.INITIAL,
    # Main
    "03": DeviceState.MAIN,
}


async def get_available_devices() -> List[IDevice]:
    port_list = serial.tools.list_ports.comports()
    devices: List[IDevice] = []

    for port_param in port_list:
        vendor_id = getattr(port_param, "vid", None)
        product_id = getattr(port_param, "pid", None)
        serial_number = getattr(port_param, "serial_number", None)
        path = port_param.device

        # Convert vendor_id and product_id to strings for comparison
        vendor_id_str = f"{vendor_id:04x}" if vendor_id is not None else None
        product_id_str = f"{product_id:04x}" if product_id is not None else None

        if (
            vendor_id_str
            and product_id_str
            and serial_number
            and vendor_id_str in ["3503"]
        ):

            internal_hardware_version = product_id_str[0:2]
            internal_device_state = product_id_str[2:4]

            # Check if the PID is valid
            if (
                internal_hardware_version == "01"
                and internal_device_state in supported_versions_to_device_state
            ):
                devices.append(
                    {
                        "path": path,
                        "device_state": supported_versions_to_device_state[
                            internal_device_state
                        ],
                        "serial": serial_number,
                        "vendor_id": vendor_id,
                        "product_id": product_id,
                        "type": ConnectionTypeMap.SERIAL_PORT.value,
                    }
                )

    return devices
