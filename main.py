from PyQt6.QtGui import QCloseEvent, QKeyEvent, QShowEvent
import tftpy
import os
from PyQt6.QtWidgets import  QApplication , QWidget, QLabel, QPushButton, QVBoxLayout, QApplication, QMainWindow
from PyQt6 import QtCore
from ui import Ui_SetupRouter
from PyQt6.QtCore import Qt , pyqtSignal, QThread , QMutex, QMutexLocker
import serial.tools.list_ports
import re
import json



# sudo nano /etc/network/if-up.d/add_alias_ip


class RouterSerialThread(QThread):
    data_received = pyqtSignal(str)  

    def __init__(self, router_serial= None, parent=None):
        super().__init__(parent)
        self.router_serial = router_serial
        self.running = True

    def run(self):
        while self.running:
            if self.router_serial and self.router_serial.is_open:
                try:
                    data = self.router_serial.readline().decode('utf-8').strip()
                    if data:
                        self.data_received.emit(data)
                except Exception as ex:
                    print('Exception in Router Thread' , ex)
                
    
    def stop(self):
        self.running = False
        self.wait()

class TftpServerThread(QThread):
    status_update = pyqtSignal(str)

    def __init__(self, server_address, server_directory,server_port, parent=None):
        super().__init__(parent)
        self.server_address = server_address
        self.server_directory = server_directory
        self.server = tftpy.TftpServer(self.server_directory)
        self.port = server_port
        self.running = False

    def run(self):
        self.running = True
        
        try:
            self.status_update.emit("Starting TFTP server...")
            self.status_update.emit(f"TFTP Server is running on {self.server_address}:{self.port}")
            
            self.server.listen(self.server_address, self.port)
            while self.running:
                self.msleep(100)  
        except Exception as e:
            print('Exception in TFTP Server ', e)
            
            self.status_update.emit(f"An error occurred while running the TFTP server: {e}")
        finally:
            self.stop_server()

    def stop_server(self):
        if self.running:
            self.running = False
            self.status_update.emit("Stopping TFTP server...")
            self.server = None

    def stop(self):
        self.stop_server()
        self.quit()  

class SmallPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Popup layout
        layout = QVBoxLayout()
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: white; font-size : 15px;")
        layout.addWidget(self.message_label)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                padding: 5px;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        # Set the layout
        self.setLayout(layout)
        self.setStyleSheet("background-color: black; border-radius: 10px;")
        self.adjustSize()
        
    def show_popup(self,message):
        if self.parent():
            self.message_label.setText(message)
            parent_rect = self.parent().geometry()
            popup_rect = self.geometry()
            x = parent_rect.left() + (parent_rect.width() - popup_rect.width()) // 2
            y = parent_rect.top() + (parent_rect.height() - popup_rect.height()) // 2
            self.move(x, y)
        self.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SetupRouter()  
        self.ui.setupUi(self)
        self.popup = SmallPopup(self)
        self.config = self.load_Json()
        self.initialize()
        self.list_Com_Ports()
        self.ui.tftp_save.clicked.connect(self.save_config)
        
    # Seperate Thread 
        self.route_serial_thread = None
        self.tftp_thread = None
        self.route_serial_thread = RouterSerialThread()
        
        
    # PySerial Router
        self.router_serial = None
        self.ui.connect_router.clicked.connect(self.pyserial_router_connect)
        self.ui.send_to_router_serial.clicked.connect(self.send_to_router_pyserial)
        self.ui.send_to_gsm_serial.clicked.connect(self.send_to_gsm_pyserial)
        self.ui.clear_router_serial.clicked.connect(self.clear_router_pyserialText)
    
    # Pyserial Gsm 
        self.ui.clear_gsm_serial.clicked.connect(self.clear_router_pyserialText)
        
    # Send Commands to the PySerial 
        self.ui.send_router_1.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.router_command_1,self.ui.router_pyserial))
        self.ui.send_router_2.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.router_command_2,self.ui.router_pyserial))
        self.ui.send_router_3.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.router_command_3,self.ui.router_pyserial))
        self.ui.send_router_4.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.router_command_4,self.ui.router_pyserial))
        
        self.ui.send_gsm_1.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.gsm_command_1,self.ui.gsm_pyserial))
        self.ui.send_gsm_2.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.gsm_command_2,self.ui.gsm_pyserial))
        self.ui.send_gsm_3.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.gsm_command_3,self.ui.gsm_pyserial))
        self.ui.send_gsm_4.clicked.connect(lambda : self.get_text_send_to_pyserial(self.ui.gsm_command_4,self.ui.gsm_pyserial))
    
        self.start_tftp_server()
        
    def start_tftp_server(self):
        if self.tftp_thread is not None:
            self.tftp_thread.stop()
            self.tftp_thread.wait()  # 
            
            
        tftp = self.config.get('Tft_Ip')
        self.tftp_thread = TftpServerThread(
            server_address=tftp.get('TFTIP'),
            server_directory=os.getcwd(),
            server_port=tftp.get('TFTP_PORT'),
            )
        self.tftp_thread.status_update.connect(self.send_to_tftp_pyserial)
        
        self.tftp_thread.start()
        
    def load_Json(self):
        
        with open('config.json', 'r') as file:
            data = json.load(file) 
            structured_data = {
                    "Router" : data.get('Router'),
                    "Gsm": data.get('Gsm'),
                    "Tft_Ip": data.get('Tft_Ip'),
                    "Voltage": data.get('Voltage'),
                }
        
        return structured_data
                
    def list_Com_Ports(self):
        ports = serial.tools.list_ports.comports()
        # print(ports)
        
        for port in ports:
            print(port.device)
            
            self.ui.gsm_port_list.addItem(port.device)
            self.ui.router_port_list.addItem(port.device)
            self.ui.voltage_port_likst.addItem(port.device)
            
        # com_port = self.config['Router'].get('tty_com_port')
        # if com_port:
        #     self.ui.router_port_list.setCurrentText(com_port)
    
    def connect_to_serial_port(self,port,boudrate):

        try:
            ser = serial.Serial(port, boudrate, timeout=1)  
            return True, ser
        except serial.SerialException as e:
            
            return False ,e
    
    def display_in_router_pyserial(self,data):
        self.ui.router_pyserial.append(data)

    def send_to_router_pyserial(self):
        
        input_txt = self.ui.router_serial_input.text()
                
        if self.route_serial_thread:
            self.route_serial_thread.router_serial.write(input_txt.encode('utf-8'))
            
        self.ui.router_pyserial.append(input_txt)
        
    def clear_router_pyserialText(self):
        self.ui.router_pyserial.clear()
        
        if self.route_serial_thread:
            self.route_serial_thread.router_serial.reset_input_buffer()
            self.route_serial_thread.router_serial.reset_output_buffer()
    
    def clear_gsm_pyserialText(self):
        self.ui.gsm_pyserial.clear()
        
        
    def send_to_gsm_pyserial(self):
        input_txt = self.ui.gsm_serial_input.text()
        self.ui.gsm_pyserial.append(input_txt)
        
    def send_to_tftp_pyserial(self,data):
        if data:
            self.ui.tftp_serial.append(data)
    
    def pyserial_router_connect(self):
        self.route_serial_thread.start()
        port = self.ui.router_port_list.currentText()
        
        if not port:
            self.popup.show_popup("Port Not Selected.")
            return
        
        print('port',port)
        
        # port = re.sub(r'[()]', '', port.split()[-1])
        boud_rate = self.config.get('Router').get('ROUTER_BAUD_RATE')
        status,serial = self.connect_to_serial_port(port,boud_rate)
        
        if not status:
            print("Exception ", serial)
            self.ui.router_pyserial.setText("Serial Not Running")
            return
        
        self.ui.router_pyserial.clear()

        self.route_serial_thread.router_serial = serial
        self.route_serial_thread.data_received.connect(self.display_in_router_pyserial)
            

    def initialize(self):
        # Router Commands
        self.ui.router_command_1.setText(self.config.get("Router").get('COMM_1'))
        self.ui.router_command_2.setText(self.config.get("Router").get('COMM_2'))
        self.ui.router_command_3.setText(self.config.get("Router").get('COMM_3'))
        self.ui.router_command_4.setText(self.config.get("Router").get('COMM_4'))
        
        # GSM Commands
        self.ui.gsm_command_1.setText(self.config.get("Gsm").get('COMM_1'))
        self.ui.gsm_command_2.setText(self.config.get("Gsm").get('COMM_2'))
        self.ui.gsm_command_3.setText(self.config.get("Gsm").get('COMM_3'))
        self.ui.gsm_command_4.setText(self.config.get("Gsm").get('COMM_4'))
        
        #TFTP Config
        self.ui.tftp_ip_input.setText(self.config.get("Tft_Ip").get('TFTIP'))
        self.ui.tftp_name_input.setText(self.config.get("Tft_Ip").get('FILE_PATH'))
        self.ui.tftp_path_input.setText(self.config.get("Tft_Ip").get('FILE_NAME'))
        
        
        
    def get_text_send_to_pyserial(self,command,pyserial):
        text = command.text()

        if self.route_serial_thread:
            self.route_serial_thread.router_serial.write(text.encode('utf-8'))
        
            pyserial.append(text)
    
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            
            print('Text ', self.ui.router_serial_input.text())
            
            if self.ui.router_serial_input.hasFocus():
                self.send_to_router_pyserial()
                                    
                if not self.ui.router_serial_input.text():
                    self.route_serial_thread.router_serial.write(b'\n')
                
                self.ui.router_serial_input.clear()
            
            if self.ui.gsm_serial_input.hasFocus():
                self.send_to_gsm_pyserial()
                
                self.ui.gsm_serial_input.clear()
                
            if self.ui.router_command_1.hasFocus():
                self.get_text_send_to_pyserial(self.ui.router_command_1, self.ui.router_pyserial)
                
            if self.ui.router_command_2.hasFocus():
                self.get_text_send_to_pyserial(self.ui.router_command_2, self.ui.router_pyserial)
                
            if self.ui.router_command_3.hasFocus():
                self.get_text_send_to_pyserial(self.ui.router_command_3, self.ui.router_pyserial)
                
            if self.ui.router_command_4.hasFocus():
                self.get_text_send_to_pyserial(self.ui.router_command_4, self.ui.router_pyserial)
            
            if self.ui.gsm_command_1.hasFocus():
                self.get_text_send_to_pyserial(self.ui.gsm_command_1, self.ui.gsm_pyserial)
                
            if self.ui.gsm_command_2.hasFocus():
                self.get_text_send_to_pyserial(self.ui.gsm_command_2, self.ui.gsm_pyserial)
                
            if self.ui.gsm_command_3.hasFocus():
                self.get_text_send_to_pyserial(self.ui.gsm_command_3, self.ui.gsm_pyserial)
                
            if self.ui.gsm_command_4.hasFocus():
                self.get_text_send_to_pyserial(self.ui.gsm_command_4, self.ui.gsm_pyserial)
  
    def save_config(self):
        if not self.config:
            self.popup.show_popup("Config Json Missing..")
            return
        
        self.config.get('Tft_Ip').update({
            'TFTIP' : self.ui.tftp_ip_input.text(),
            'FILE_PATH': self.ui.tftp_path_input.text(),
            'FILE_NAME': self.ui.tftp_name_input.text(),
        })
        
        # with open('config.json', 'w') as json_file:
        #     json.dump(self.config, json_file, indent=4)
        
        self.save()

        print(self.tftp_thread.isRunning())
        
        if self.tftp_thread.isRunning():
            self.tftp_thread.stop()
        
        self.ui.tftp_serial.clear()
        self.ui.tftp_serial.append('Restarting TFTP Server')
        self.start_tftp_server()
        
        self.popup.show_popup("Config Json Updated.!")
        
    def closeEvent(self, event) -> None:
        
        if self.route_serial_thread and self.route_serial_thread.isRunning():
            
            self.route_serial_thread.stop()
            self.route_serial_thread.wait()
            print('Closed Router Thread')
    
    def save(self):
        with open('config.json', 'w') as json_file:
            json.dump(self.config, json_file, indent=4)

    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

