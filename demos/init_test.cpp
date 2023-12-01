//
// Created by koondra on 1.12.23.
//

#include <sys/socket.h>
#include <iostream>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>

#define SOCKET_DOMAIN AF_INET // local network
#define SOCKET_TYPE SOCK_DGRAM // sets UDP protocol
#define SOCKET_PROTOCOL 0 // sets IP protocol

using namespace std;


bool create_udp_socket(int *socket_fd){
    int temp_socket_fd = socket(SOCKET_DOMAIN, SOCKET_TYPE, SOCKET_PROTOCOL);
    if(temp_socket_fd < 0){
        cout << "Unable to open the socket" << endl;
        return false;
    }

    *socket_fd = temp_socket_fd;
    return true;
}

bool open_server(uint16_t port, char *ip_address, int *server_fd){

    // create the server adress
    struct sockaddr_in server_adress;
    server_adress.sin_family = AF_INET; // set to local network
    server_adress.sin_port = htons(port);
    server_adress.sin_addr.s_addr = inet_addr(ip_address);
    //server_adress.sin_addr.s_addr = INADDR_ANY;

    // get the server socket
    int server_socket_fd;
    bool ret = create_udp_socket(&server_socket_fd);
    if(!ret){
        cerr << "Unable to open socket for the server" << endl;
        exit(EXIT_FAILURE);
    }
    else{
        cout << "Successfully opened server's socket" << endl;
    }

    // bind the server's socket to its address
    ret = bind(server_socket_fd, (struct sockaddr*)&server_adress, sizeof(struct sockaddr)) != -1;
    if(!ret){
        cerr << "Unable to bind server socket to address" << endl;
        close(server_socket_fd);
        exit(EXIT_FAILURE);
    }

    *server_fd = server_socket_fd;

    return ret;
}




int main(){

    char ip[] = "192.168.1.2";
    int server_fd;
    bool ret = open_server(8080, ip, &server_fd);
    if(ret){
        cout << "Success" << endl;
    }


    // Get the address of the socket
    struct sockaddr_in addr;
    socklen_t len = sizeof(addr);
    int test_ret = getsockname(server_fd, (struct sockaddr *)&addr, &len);
    cout << test_ret << endl;
    // Convert the IP address to a string
    char ipstr[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &addr.sin_addr, ipstr, sizeof(ipstr));

    // Print the IP address and the port number
    std::cout << "The socket is bound to " << ipstr << ":" << ntohs(addr.sin_port) << std::endl;


    return 0;
}


