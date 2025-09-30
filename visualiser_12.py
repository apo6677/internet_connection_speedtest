import matplotlib.pyplot as plt
import numpy as np

def calculate_windowed_mean(timestamps, values):
    window_size=2
    num_windows = 15
    window_means = []
    window_centers = []
    
    for i in range(num_windows):
        start = i * window_size
        end = (i + 1) * window_size
        mask = (timestamps >= start) & (timestamps < end)
        window_values = np.array(values)[mask]
        if len(window_values) > 0:
            window_means.append(np.mean(window_values))
        else:
            window_means.append(0.0)

        window_centers.append(start + window_size / 2)
    
    return window_centers, window_means
##########################################################################################################################
#-------------------------------------------------------------------------------------------------------------------------
##########################################################################################################################

def visualiser_12(throughput_data_file, av_throughput_data, rate_gap_file, throughput_params, rates,RSSI_file):

    visual_rate_gap = dict()

    throughputs = dict()

    timestamps = []
    frames_loss = []
    data_rates = []

############################################################################################################################
#----------------------------------------------------Data extraction-------------------------------------
############################################################################################################################
    RSSI_timestamps =[]
    RSSI = []
    with open(RSSI_file,"r") as rssi_file:
        for line in rssi_file:
            data = line.strip().split('::')

            RSSI_timestamps.append(float(data[0]))
            RSSI.append(float(data[1]))


    seconds = []
    client_server_rate = []
    with open("client_server_2.4ghz_moving.txt","r") as client_server:
        for line in client_server:
            data = line.strip().split('::')

            seconds.append(float(data[0]))
            client_server_rate.append(float(data[1]))

    seconds_iperf = []
    iperf_rate = []
    with open("iperf_2.4ghz_moving.txt","r") as iperf:
        for line in iperf:
            data = line.strip().split('::')

            seconds_iperf.append(float(data[0]))
            iperf_rate.append(float(data[1]))

    with open(rates,"r") as ratess:
            for line in ratess:
                data = line.strip().split('::')

                timestamps.append(float(data[0]))
                data_rates.append(float(data[1]))
                frames_loss.append(float(data[2]))

    with open(throughput_params,"r") as params:
            for line in params:
                data = line.strip().split('::')
                colision_factor = float(data[0])
                mac_eff = float(data[1])

    with open(throughput_data_file,"r") as throughput_file:
        for line in throughput_file:
            data = line.strip().split('::')

            timestamp = float(data[0])
            throughput = float(data[1])

            throughputs[timestamp] = throughput

    with open(rate_gap_file,"r") as rate_gap:
        for line in rate_gap:
            data = line.strip().split('::')

            timestamp = float(data[0])
            rate_gap = float(data[1])

            visual_rate_gap[timestamp] = rate_gap

    
    print(f"Total Frames: {av_throughput_data[0]}")
    print(f"Lost Frames: {av_throughput_data[1]}")
    print(f"Frame Loss Rate: {av_throughput_data[2]:.2%}")
    print(f"Average Data Rate (Mbps): {av_throughput_data[3]:.2f}")
    print(f"Average Theoretical Throughput by wifi doctor (Mbps): {av_throughput_data[4]:.2f}")

############################################################################################################################
#----------------------------------------------------Throughput and Rate gap plots across time----------------------------
############################################################################################################################
    # Process data rate data
    data_rate_timestamps = np.array(timestamps) - min(timestamps)
    dr_windows, data_rates_values = calculate_windowed_mean(data_rate_timestamps, data_rates)

    # Process Rate Gap data
    rate_gap_timestamps = np.array(list(visual_rate_gap.keys())) - min(visual_rate_gap.keys())
    rate_gap_values = list(visual_rate_gap.values())
    rg_windows, rg_means = calculate_windowed_mean(rate_gap_timestamps, rate_gap_values)

    # Process Throughput data
    throughput_timestamps = np.array(list(throughputs.keys())) - min(throughputs.keys())
    throughput_values = list(throughputs.values())
    tp_windows, tp_means = calculate_windowed_mean(throughput_timestamps, throughput_values)

    revised_throughput_means = [tp_mean*colision_factor*mac_eff for tp_mean in tp_means]

    # Plotting
    plt.figure(1, figsize=(12, 6))  # Wider figure for better visibility

    # Plot all four datasets with distinct styles
    plt.plot(seconds, client_server_rate, 'r-', label='Client-Server Throughput (Real-time)', linewidth=2)
    plt.plot(seconds_iperf, iperf_rate, 'g--', label='iperf Throughput', linewidth=2)
    plt.plot(tp_windows, revised_throughput_means, 'b-o', label='Revised Throughput', markersize=6, linewidth=1)
    plt.plot(tp_windows, tp_means, 'c-s', label='WiFi Doctor Estimate', markersize=5, linewidth=1)

    # Formatting
    plt.title("Throughput Comparison when moving at 2.4ghz", fontsize=14)
    plt.xlabel("Time (s)", fontsize=12)
    plt.ylabel("Throughput (Mbps)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10, framealpha=1)

    # Adjust x-axis if needed (use the broadest time range)
    all_times = list(seconds) + list(seconds_iperf) + list(tp_windows)
    plt.xlim(min(all_times), max(all_times))

    plt.tight_layout() 

    # Create subplots with consistent styling
    plt.figure(figsize=(12, 12))  # Single figure for all plots

    # Plot 1: Rate Gap
    plt.subplot(4, 1, 1)
    plt.plot(rg_windows, rg_means, 'b-o', linewidth=2, markersize=6, label='Rate Gap')
    plt.title("Rate Gap (2s window means)", fontsize=10)
    plt.ylabel("Mbps", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Plot 2: Data Rate
    plt.subplot(4, 1, 2)
    plt.plot(dr_windows, data_rates_values, 'c-o', linewidth=2, markersize=6, label='Data Rate')
    plt.title("Data Rate", fontsize=10)
    plt.ylabel("Mbps", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Plot 3: Frame Loss
    plt.subplot(4, 1, 3)
    plt.plot(timestamps, frames_loss, 'r-', linewidth=1.5, label='Frame Loss')
    plt.title("Frame Loss Over Time", fontsize=10)
    plt.ylabel("Loss Count", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Plot 4: RSSI
    plt.subplot(4, 1, 4)
    plt.plot(RSSI_timestamps, RSSI, 'r-', linewidth=1.5, label='RSSI')
    plt.title("RSSI Over Time", fontsize=10)
    plt.xlabel("Time (s)", fontsize=9)
    plt.ylabel("RSSI", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    plt.tight_layout(pad=2.0)  # Better spacing between subplots
    plt.show()