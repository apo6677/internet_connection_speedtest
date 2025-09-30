import pyshark

def parser_12(throughput_file):

    throughput_data_files = []

    data_frames = dict()
    lost_frames = dict()

    signal_strength = 0
    short_gi = None

    cap = pyshark.FileCapture(throughput_file, display_filter="wlan.fc.type_subtype == 40 && wlan.ta == 94:a7:b7:24:4a:52 && wlan.da == e6:60:21:65:8c:fb" , use_json=True)

    for pkt in cap:
        timestamp = float(pkt.sniff_timestamp)
        duration = int(pkt.wlan_radio.duration) if hasattr(pkt.wlan, 'duration') else 0
        data_rate = float(pkt.wlan_radio.data_rate)  if hasattr(pkt, "wlan_radio") and hasattr(pkt.wlan_radio, "data_rate") else 0
        signal_strength = pkt.wlan_radio.signal_dbm if hasattr(pkt.wlan_radio, 'signal_dbm') else 7
        short_gi = pkt.wlan_radio.short_gi if hasattr(pkt.wlan_radio, 'short_gi') else None
        frame_len = int(pkt.length)*8 if hasattr(pkt, "wlan") else 0
        if hasattr(pkt.data, 'data'):
            hex_string = pkt.data.data.replace(':', '')  # Remove colons if any
            payload_len = len(hex_string) // 2 * 8  # Each hex pair = 1 byte
        else:
            payload_len = 0
        if data_rate!=0 and signal_strength != 0 and short_gi is not None:
            data_frames[timestamp] = {"data_rate": data_rate, "RSSI": signal_strength, "short_gi": short_gi, "len": frame_len, "payload": payload_len, "duration": duration} 
        else: pass
    cap.close()

    throughput_data_file = f"throughput_file.txt"

    throughput_data_files.append(throughput_data_file)

    with open(throughput_data_file, "w", encoding="utf-8") as throughput_data:
            for timestamp in data_frames.keys():
                throughput_data.write(str(timestamp) +"::"+str(data_frames[timestamp]["data_rate"])+"::"+str(data_frames[timestamp]["RSSI"]) +"::"+str(data_frames[timestamp]["short_gi"])+"::"+str(data_frames[timestamp]["len"])+ "::"+str(data_frames[timestamp]["payload"])+"::"+str(data_frames[timestamp]["duration"])+'\n')

    
    
    cap = pyshark.FileCapture(throughput_file, display_filter= "wlan.fc.retry == 1 &&wlan.ta == 94:a7:b7:24:4a:52 && wlan.da == e6:60:21:65:8c:fb", use_json=True)

    for pkt in cap:
        timestamp = float(pkt.sniff_timestamp)
        data_rate = float(pkt.wlan_radio.data_rate)  if hasattr(pkt, "wlan_radio") and hasattr(pkt.wlan_radio, "data_rate") else 0 
        lost_frames[timestamp] = data_rate
        
    cap.close()

    throughput_data_file = f"frame_loss_file.txt"

    throughput_data_files.append(throughput_data_file)

    with open(throughput_data_file, "w", encoding="utf-8") as throughput_data:
            for timestamp in lost_frames.keys():
                throughput_data.write(str(timestamp) +"::"+str(lost_frames[timestamp])+ '\n')


    return throughput_data_files