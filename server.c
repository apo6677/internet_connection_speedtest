// server.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <arpa/inet.h>

#define PORT 5000
#define BUFFER_SIZE 8192
#define EXPERIMENT_DURATION 30
#define REPORT_INTERVAL 2

void handle_client(int client_socket) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_received;
    size_t total_received = 0;
    time_t start_time = time(NULL);
    time_t last_report_time = start_time;

    printf("Client connected.\n");

    while (1) {
        bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
        if (bytes_received <= 0) break;

        total_received += bytes_received;
        time_t now = time(NULL);

        if (now - last_report_time >= REPORT_INTERVAL) {
            double mbits = (total_received * 8.0) / 1e6;
            printf("Received %.2f Mbps in last %d seconds\n", mbits / (now - last_report_time), REPORT_INTERVAL);
            total_received = 0;
            last_report_time = now;
        }

        if (now - start_time >= EXPERIMENT_DURATION) {
            break;
        }
    }

    double total_mbits = (total_received * 8.0) / 1e6;
    printf("Client disconnected. Aggregated throughput: %.2f Mbps\n", total_mbits / EXPERIMENT_DURATION);
    close(client_socket);
}

int main() {
    int server_fd, client_socket;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 1) < 0) {
        perror("Listen");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    while (1) {
        client_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
        if (client_socket < 0) {
            perror("Accept");
            continue;
        }
        handle_client(client_socket);
    }

    return 0;
}
