import socket
import signal
import sys
import threading
import time

message_list = []  # Mesajları tutacak liste
lock = threading.Lock()  # Erişim senkronizasyonu için lock
running = True  # Programın çalışıp çalışmadığını kontrol eden bayrak
slot_data = {}  # Slot numaralarına göre verileri tutacak sözlük
voltage_values_for_all_slots = {}  # Tüm slotlar için voltaj değerlerini tutacak sözlük

# Sunucuyu düzgün kapatmak için bir sinyal işleyicisi
def signal_handler(sig, frame):
    global running
    print('Sunucu kapatılıyor...')
    running = False
    print(slot_data)
    print(voltage_values_for_all_slots)
    sock.close()


signal.signal(signal.SIGINT, signal_handler)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 12345))
sock.listen(5)
sock.settimeout(1)  # Accept çağrısına zaman aşımı eklendi

print("Sunucu çalışıyor... (Ctrl+C ile kapatabilirsiniz)")

def message_receiver():
    global running
    while running:
        try:
            connection, address = sock.accept()
            buf = connection.recv(1024)
            if buf:
                print(f"Received: {buf}")
                with lock:
                    message_list.append(buf)  # Mesaj listeye eklendi.
            connection.close()
        except socket.timeout:
            continue  # Zaman aşımında döngüye devam edin
        except OSError:
            break

def message_processor():
    global running
    while running:
        with lock:
            if message_list:
                msg = message_list.pop(0)  # İlk mesajı al
                process_message(msg)
               
            
        #time.sleep(0.1)  # Çok hızlı döngü olmasın
def process_message(msg):
    if len(msg) < 5:
        print("Mesaj 5 bytedan küçük, işlenmiyor.")
        return

    slot_no = msg[1] - 32
    if slot_no < 1 or slot_no > 10:
        print("Geçersiz slot numarası, işlenmiyor.")
        print(slot_no)
        return

    data_length = msg[3]
    if len(msg) < 4 + data_length:
        print("Veri uzunluğu yetersiz, işlenmiyor.")
        return

    data = msg[4:4 + data_length]
    if slot_no not in slot_data:
        slot_data[slot_no] = []

    slot_data[slot_no].append(data)


        
    print(f"Slot {slot_no} verisi: {data}")

        # Her slot için voltaj değerlerini hesapla
    calculate_voltage(slot_no)

def calculate_voltage(slot_no):
    # Her veri parçası için kanalların sayısını dinamik olarak belirleyeceğiz
    for data in slot_data[slot_no]:
        print(len(data))
        num_channels = len(data) // 5
        
         # Eğer voltage_values_for_all_slots bu slot için henüz tanımlanmamışsa dinamik olarak oluştur
        if slot_no not in voltage_values_for_all_slots:
            voltage_values_for_all_slots[slot_no] = [[] for _ in range(num_channels)]


        # Kanallara göre voltaj hesaplamalarını yap ve sakla
        for j in range(num_channels):
            kanal = data[j*5:(j+1)*5]  # 5 byte'lık kanal verisini al
            if len(kanal) < 5:
                continue
            
            # Bitwise işlemleri kullanarak signed int16 değerini çıkar
            signed_int16 = (kanal[1] << 8) | kanal[2]
            if signed_int16 >= 32768:
                signed_int16 -= 65536  # Signed integer conversion
            
            voltage = (signed_int16 * 20 / 65535) - 10
            voltage_values_for_all_slots[slot_no][j].append(voltage)


receiver_thread = threading.Thread(target=message_receiver)
processor_thread = threading.Thread(target=message_processor)

receiver_thread.start()
processor_thread.start()

try:
    while running:
        time.sleep(0.01)  # Ana döngüyü çalışır durumda tutmak için uyutuyoruz
except KeyboardInterrupt:
    print("Ana döngüden çıkılıyor.")
    running = False

# Thread'lerin bitmesini bekleme
receiver_thread.join()
processor_thread.join()

print("Program sonlandı.")
