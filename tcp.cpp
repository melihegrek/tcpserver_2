#include "TCP.h"
#include <chrono>
#include <ctime>

TCP::TCP() : stopFlag(false), serverSocket(INVALID_SOCKET) {
    initializeWinsock();
}

TCP::~TCP() {
    stop();
    WSACleanup();
}

TCP& TCP::getInstance() {
    static TCP instance;
    return instance;
}

void TCP::insert(const std::vector<char>& data) {
    std::unique_lock<std::mutex> lock(mtx);
    messageQueue.push(data);
    cv.notify_one();
}

void TCP::start() {
    stopFlag = false;
    createSocket();
    connectSocket();
    workerThread = std::thread(&TCP::processQueue, this);
}

void TCP::stop() {
    {    
        std::unique_lock<std::mutex> lock(mtx);
        stopFlag = true;
    }
    cv.notify_all();

    if (workerThread.joinable()) {
        workerThread.join();
    }

    if (serverSocket != INVALID_SOCKET) {
        closesocket(serverSocket);
        serverSocket = INVALID_SOCKET;
    }
}

void TCP::processQueue() {
    while (true) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this] { return !messageQueue.empty() || stopFlag; });

        while (!messageQueue.empty()) {
            std::vector<char> message = messageQueue.front();
            messageQueue.pop();
            lock.unlock();

            // Process the message (for example, send it over a TCP connection)
            std::cout << "Sending message: ";
            for(int i=0; i<message.size();i++)
            {
                printf("%x ", message[i]);

            }
            std::cout << "\n";

            // Here you would normally send the message over the network using the serverSocket
            int sendResult = send(serverSocket, message.data(), message.size(), 0);
            if (sendResult == SOCKET_ERROR) {
                std::cerr << "send failed with error: " << WSAGetLastError() << std::endl;
                closesocket(serverSocket);
                WSACleanup();
                return;
            }

            lock.lock();
        }

        if (stopFlag && messageQueue.empty()) {
            break;
        }
    }
}

std::string TCP::getCurrentDateTime() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::tm buf;
    localtime_s(&buf, &in_time_t);
    char str[100];
    std::strftime(str, sizeof(str), "%Y-%m-%d %H:%M:%S", &buf);
    return str;
}

void TCP::initializeWinsock() {
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        std::cerr << "WSAStartup failed with error: " << iResult << std::endl;
        exit(EXIT_FAILURE);
    }
}

void TCP::createSocket() {
    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket == INVALID_SOCKET) {
        std::cerr << "socket failed with error: " << WSAGetLastError() << std::endl;
        WSACleanup();
        exit(EXIT_FAILURE);
    }
}

void TCP::connectSocket() {
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port); // Port numarası kullanılıyor
    serverAddr.sin_addr.s_addr = inet_addr(ipAddress.c_str()); // IP adresi kullanılıyor

    int iResult = connect(serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr));
    if (iResult == SOCKET_ERROR) {
        std::cerr << "connect failed with error: " << WSAGetLastError() << std::endl;
        closesocket(serverSocket);
        WSACleanup();
        exit(EXIT_FAILURE);
    }
    std::cout << "Connection Successful.\n";
}

void TCP::setIpAddress(const std::string& ipAddress) {
    this->ipAddress = ipAddress;
}

void TCP::setPort(int port) {
    this->port = port;
}
