from pypxe import tftp

import os


server_settings = {
    'netboot_directory' : os.path.join(os.getcwd() , "root")
}

tftpy = tftp.TFTPD(**server_settings)

tftpy.listen()