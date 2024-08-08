import socket
import signal
import sys
import threading

message_list = []                         # Mesajları tutacak listemiz.
condition = threading.Condition()         # cv kullanacağız...
shutdown_flag = threading.Event()         # Sunucuyu kapatmak için bir bayrak

# Mesajları listeye ekleyen iş parçacığı
def message_receiver(sock):
    while not shutdown_flag.is_set():
        try:
            connection, address = sock.accept()
            buf = connection.recv(1024)
            if buf:
                print(f"Received: {buf}")
                with condition:
                    message_list.append(buf)
                    condition.notify()  # Yeni bir mesaj eklendiğini işaretle
                    
        except socket.timeout:
            continue
        except OSError:
            break

# Mesajları işleyen iş parçacığı
def message_processor():
    while not shutdown_flag.is_set():
        with condition:
            while not message_list and not shutdown_flag.is_set():
                condition.wait()  # Mesaj listesinde yeni mesaj olmasını bekle
            if message_list:
                message = message_list.pop(0)
                # Burada mesaj üzerinde işlem yapabilirsiniz
                print(f"Processing: {message}")

# Sunucuyu düzgün kapatmak için bir sinyal işleyicisi
def signal_handler(sig, frame):
    print('Sunucu kapatılıyor...')
    shutdown_flag.set()
    with condition:
        condition.notify_all()  # Tüm iş parçacıklarını uyandır
    sock.close()

signal.signal(signal.SIGINT, signal_handler)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 12345))
sock.listen(5)

print("Sunucu çalışıyor... (Ctrl+C ile kapatabilirsiniz)")

# İş parçacıklarını başlat
receiver_thread = threading.Thread(target=message_receiver, args=(sock,))
processor_thread = threading.Thread(target=message_processor)

receiver_thread.start()
processor_thread.start()

# Ana programı beklet
receiver_thread.join()
processor_thread.join()

print("Sunucu kapandı.")