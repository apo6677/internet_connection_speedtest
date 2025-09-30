import pyshark
import time
import subprocess

def set_channel(interface, channel):
    try:
        subprocess.run(["sudo", "iwconfig", interface, "channel", str(channel)], check=True)
        print(f"Interface {interface} set to channel {channel}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set channel {channel} on {interface}: {e}")

def wifi_sniffer(interface='wlan0', duration=10, output_file='current_network_traffic.pcapng', capture_filter=""):
    """
    Capture 802.11 packets in monitor mode using pyshark.LiveCapture.

    Parameters:
      interface (str): Wi-Fi interface to capture on.
      duration (int): Capture duration in seconds.
      output_file (str): Filename to save the capture.
      capture_filter (str): (Optional) BPF capture filter for 802.11 frames.

    Returns:
      str: The output file name.
    """
    # The custom_parameters flag "-I" instructs tshark to enable monitor mode.
    capture = pyshark.LiveCapture(
        interface=interface,
        output_file=output_file,
        capture_filter=capture_filter,  # e.g., "wlan type mgt" for management frames if needed
        custom_parameters=["-I"]
    )
    capture.sniff(timeout=duration)
    print(f"Capture complete, saved to {output_file}")
    return output_file

def channel_sniffer(interface, channels, dwell_time=10, output_prefix="live_capture"):
    """
    Capture packets from multiple channels by channel hopping.

    Parameters:
      interface (str): The wireless interface in monitor mode (e.g., wlan0mon).
      channels (list): List of channels to hop through.
      dwell_time (int): Capture time per channel in seconds.
      output_prefix (str): Prefix for the generated capture files.

    Returns:
      list: List of capture file names for each channel.
    """
    capture_files = []
    for channel in channels:
        set_channel(interface, channel)
        # Give the interface a moment to switch channels.
        time.sleep(1)
        output_file = f"{output_prefix}_ch{channel}.pcapng"
        print(f"Capturing on channel {channel} for {dwell_time} sec...")
        wifi_sniffer(interface=interface, duration=dwell_time, output_file=output_file, capture_filter="")
        capture_files.append(output_file)
    return capture_files
