#include "TCP.h"
#include <vector>
#include <thread>
#include <chrono>

int main() {
    TCP& client = TCP::getInstance();
    client.setIpAddress("127.0.0.1"); // IP adresini ayarlayın
    client.setPort(12345); // Port numarasını ayarlayın

    client.start();

    // Mesajın oluşturulması
    std::vector<char> message;
    message.push_back(0x5A); // Başlangıç baytı
    message.push_back(0x23); // Slot numarası
    message.push_back(0xB1);//tip
    message.push_back(0x14); // Veri uzunluğu

    message.push_back(0x17); 
    message.push_back(0x02); 
    message.push_back(0x07); 
    message.push_back(0xE1); 
    message.push_back(0x17); 
    
    message.push_back(0x02); 
    message.push_back(0x07); 
    message.push_back(0xE1);
    message.push_back(0x17); 
    message.push_back(0x02); 
    
    message.push_back(0x07); 
    message.push_back(0xE1);
    message.push_back(0x17); 
    message.push_back(0x02); 
    message.push_back(0x07); 
    message.push_back(0xE1);
    message.push_back(0x17); 
    message.push_back(0x02); 
    message.push_back(0x07); 
    message.push_back(0xE1);

    message.push_back(0x6C); //crc
    client.insert(message);

    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    client.stop();
    return 0;
}
