#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <arpa/inet.h>
#include <errno.h>

#define SERVER_IP "192.168.1.7"
#define PORT 8080
#define BUFFER_SIZE 8192
#define EXPERIMENT_DURATION 30
#define REPORT_INTERVAL 2

int main() {
    int sock;
    struct sockaddr_in server_address;
    char buffer[BUFFER_SIZE];
    memset(buffer, 'A', BUFFER_SIZE);

    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);

    if (inet_pton(AF_INET, SERVER_IP, &server_address.sin_addr) <= 0) {
        fprintf(stderr, "Invalid address/Address not supported: %s\n", SERVER_IP);
        close(sock);
        exit(EXIT_FAILURE);
    }

    printf("Attempting to connect to %s:%d...\n", SERVER_IP, PORT);

    int retry = 3;
    while (retry--) {
        if (connect(sock, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
            fprintf(stderr, "Connection attempt failed (retries left: %d): %s\n", 
                    retry, strerror(errno));
            if (retry > 0) {
                sleep(1);
                continue;
            }
            close(sock);
            exit(EXIT_FAILURE);
        }
        break;
    }

    printf("Successfully connected to server!\n");
    printf("Starting data transmission for %d seconds...\n", EXPERIMENT_DURATION);

    time_t start_time = time(NULL);
    time_t last_report_time = start_time;
    size_t total_sent = 0;

    while (1) {
        ssize_t sent = send(sock, buffer, BUFFER_SIZE, 0);
        if (sent < 0) {
            perror("Send failed");
            break;
        }

        total_sent += sent;
        time_t now = time(NULL);

        if (now - last_report_time >= REPORT_INTERVAL) {
            double mbits = (total_sent * 8.0) / 1e6;
            printf("[%ds] Sent %.2f Mbps (total: %.2f MB)\n", 
                   (int)(now - start_time), 
                   mbits / (now - last_report_time),
                   total_sent / 1e6);
            total_sent = 0;
            last_report_time = now;
        }

        if (now - start_time >= EXPERIMENT_DURATION) {
            printf("Experiment duration reached.\n");
            break;
        }
    }

    close(sock);
    printf("Connection closed.\n");
    return 0;
}