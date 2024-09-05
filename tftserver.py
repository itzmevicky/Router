import tftpy
import logging

def run_tftp_server(server_directory, port=69):
    # Enable logging for TFTP server
    logging.basicConfig(level=logging.INFO)
    
    # Create a TFTP server instance
    server = tftpy.TftpServer(server_directory)
    
    try:
        # Start the TFTP server
        print(f"Starting TFTP server on port {port}...")
        server.listen('0.0.0.0', port)  # Listen on all interfaces
    except Exception as e:
        print(f"An error occurred while starting the TFTP server: {e}")

if __name__ == "__main__":
    # Specify the directory where the server will store and serve files
    server_directory = "root"  # Replace with your directory path
    
    # Run the TFTP server
    run_tftp_server(server_directory)
