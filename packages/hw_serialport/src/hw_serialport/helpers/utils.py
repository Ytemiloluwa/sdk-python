import serial


async def open_connection(connection: serial.Serial) -> None:
    if connection.is_open:
        return

    connection.open()


async def close_connection(connection: serial.Serial) -> None:
    if not connection.is_open:
        return

    connection.close()
