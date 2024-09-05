import tftpy


server_ip = '10.10.10.10'  
remote_directory = 'root' 
file_name = 'firmware.bin'  
local_file = './test/firmware_download.bin'  

# Initialize the TFTP client
client = tftpy.TftpClient(server_ip, 69)

# Download the file from the TFTP server
try:
    remote_path = f"{file_name}"
    print(f"Downloading {remote_path} from TFTP server {server_ip}...")
    
    client.download(remote_path, local_file)
    
    print(f"Download complete. File saved as {local_file}.")

except Exception as e:
    print(f"An error occurred: {e}")
