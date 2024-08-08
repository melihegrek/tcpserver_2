import threading
import time
import signal
import sys

running = True  # Programın çalışıp çalışmadığını kontrol eden bayrak

def signal_handler(sig, frame):
    global running
    print('Program kapatılıyor...')
    running = False

signal.signal(signal.SIGINT, signal_handler)

def thread_function_1():
    while running:
        print("Thread 1 çalışıyor...")
        time.sleep(1)

def thread_function_2():
    while running:
        print("Thread 2 çalışıyor...")
        time.sleep(1)

# Thread'leri başlatma
thread1 = threading.Thread(target=thread_function_1)
thread2 = threading.Thread(target=thread_function_2)

thread1.start()
thread2.start()

# Ana programın çalışır durumda kalması için uyutma döngüsü
try:
    while running:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Ana döngüden çıkılıyor.")

# Thread'lerin bitmesini bekleme
thread1.join()
thread2.join()

print("Program sonlandı.")
