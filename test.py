import serial.tools.list_ports

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    available_ports = []

    for port in ports:
        port_info = f"{port.device} - {port.description}"
        available_ports.append(port_info)

    return available_ports

import serial
import time

def connect_to_serial_port(port, baudrate):
    """
    Connects to the specified serial port and returns a serial object.

    Args:
        port: The name of the serial port (e.g., "COM1", "/dev/ttyUSB0").
        baudrate: The baud rate for communication.

    Returns:
        A serial object representing the connection.
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=1)  # Set a timeout for read operations
        print(f"Connected to serial port {port} at {baudrate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        return None

def receive_and_display_data(ser):
    """
    Receives data from the serial port and displays it to the console.

    Args:
        ser: A serial object representing the connection.
    """
    while True:
        data = ser.readline().decode().strip()
        if data:
            print(f"Received data: {data}")

def send_data(ser, data):
    """
    Sends data to the serial port.

    Args:
        ser: A serial object representing the connection.
        data: The data to be sent.
    """
    ser.write(data.encode())
    print(f"Sent data: {data}")

if __name__ == "__main__":
    port = "COM5"  
    baudrate = 57600  

    ser = connect_to_serial_port(port, baudrate)
    if ser:
        try:
            receive_and_display_data(ser)
            # Example: Send data
            send_data(ser, "Hello from Python!")
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            ser.close()
