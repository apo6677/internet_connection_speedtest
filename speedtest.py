import argparse
from parser_12 import parser_12
from monitor_12 import monitor_12
from visualiser_12 import visualiser_12
from sniffer import channel_sniffer  # Import the sniffer functionality

def main():
    # Set up command-line arguments for interface, channels, and capture duration.
    parser = argparse.ArgumentParser(
        description="WiFi Doctor - run offline analysis or online packet sniffing."
    )
    parser.add_argument(
        "--interface", type=str, help="WiFi interface to use for sniffing (e.g., wlan0)", default=None
    )
    parser.add_argument(
        "--channels",
        type=str,
        help="Comma-separated list of channels to hop through (e.g., '1,6,11')",
        default=None,
    )
    # Support both '--duration' and '--captime' as synonyms.
    parser.add_argument(
        "--duration", "--captime",
        type=int,
        help="Dwell time per channel in seconds (capture duration for each channel, default is 10)",
        default=10,
    )
    args = parser.parse_args()

    # Determine whether to run online sniffing or use offline pre-captured files.
    if args.interface and args.channels:
        # Convert comma-separated channels string to a list of integers.
        channels = [int(ch.strip()) for ch in args.channels.split(",")]
        print(f"Starting online sniffing on interface {args.interface} with channels {channels}...")
        print(f"Each channel will be captured for {args.duration} seconds.")
        # Run the channel hopping sniffer and collect capture files.
        throuput_file = channel_sniffer(args.interface, channels, dwell_time=args.duration)
    else:
        print("No interface/channels specified. Running offline analysis with pre-captured files.")
        throuput_file = "ch7_moving.pcapng"

    # Throughput analysis
    print("Parsing file")
    throughput_files = parser_12(throuput_file)
    print("Calculating Throughput")
    visual_throughput, av_throughpt, rate_gap, throughput_params, rates, RSSI_file = monitor_12(throughput_files)
    print("Plotting throughput")
    visualiser_12(visual_throughput, av_throughpt, rate_gap, throughput_params, rates,RSSI_file)

if __name__ == "__main__":
    main()
