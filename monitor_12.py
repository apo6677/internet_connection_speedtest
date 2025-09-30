def monitor_12(throughput_files):          
    
    total_frames = 0
    losses = 0
    rates = []

    data_frames = dict()
    lost_frames = dict()
    data_rates = dict()
    throughput = dict()

    rate_gaps = dict()

    total_time_air = 0
    start_time = None
    end_time = None
    total_duration = 0
    total_airtime = 0
    total_bits_captured = 0
    total_payload = 0

############################################################################################################################
#--------------------------------------------Extract data from parser and store them in---------------------------------
# ------------------------------------------the appropriately named dictionaries in order to calculate throughput----------
############################################################################################################################
    with open(throughput_files[0],"r") as throughput_file: # this is for thruoghput
        for line in throughput_file:
            data = line.strip().split('::')

            timestamp = float(data[0])
            data_rate = float(data[1])
            signal_strength = int(data[2])
            short_gi = int(data[3])
            length = int(data[4])
            duration = int(data[6])
            payload = int(data[5])
            total_frames+=1
            rates.append(data_rate)

            if data_rate > 0:
                airtime = length / (data_rate * 1e6)  # seconds

            total_duration += duration
            total_airtime += airtime

            total_bits_captured += length
            total_payload += payload

            data_frames[timestamp] = {"data_rate": data_rate, "RSSI": signal_strength, "short_gi": short_gi, "airtime": airtime}
    
    channel_util = 1e6*total_airtime/total_duration
    mac_eff = total_payload/total_bits_captured    

############################################################################################################################
#----------------------------------------------------Calculate and store rate gap in dict rate_gaps-------------------------
############################################################################################################################

    for timestamp in data_frames:
        data_rate = data_frames[timestamp]["data_rate"]
        short_gi = data_frames[timestamp]["short_gi"]

        if short_gi == 1:
            if data_rate < 156:
                rate_gaps[timestamp] = 156 - data_rate
            else: rate_gaps[timestamp] = 0
        elif short_gi ==0:
            if data_rate < 144:
                rate_gaps[timestamp] = 144 - data_rate
            else: rate_gaps[timestamp] = 0

############################################################################################################################
#----------------------------------------------------Store dictionary regarding frame loss-------------------------
############################################################################################################################
    with open(throughput_files[1],"r") as throughput_file:
        for line in throughput_file:
            data = line.strip().split('::')

            timestamp = float(data[0])
            data_rate = float(data[1])
            losses +=1
            total_frames+=1
            rates.append(data_rate)

            lost_frames[timestamp] = data_rate

######################################################################################################################
#---------------------------------Sort dictionaries regarding throughput by timestamp and------------------------
# ------------------------------- store in dictionary data_rates as well as calculate -------------------------
# --------------------------------how many packets have been lost up to the i-th timestamp ----------------
#####################################################################################################################

    L = 0
    all_timestamps = sorted(set(data_frames.keys()).union(lost_frames.keys()))

    for timestamp in all_timestamps:
        if timestamp in data_frames and timestamp in lost_frames:
            L += 1
            data_rates[timestamp] = {
                "data_rate": lost_frames[timestamp],
                "frame_losses": L
            }
        elif timestamp in data_frames:
            data_rates[timestamp] = {
                "data_rate": data_frames[timestamp]["data_rate"],
                "frame_losses": L
            }
        elif timestamp in lost_frames:
            L += 1
            data_rates[timestamp] = {
                "data_rate": lost_frames[timestamp],
                "frame_losses": L
            }

############################################################################################################################
#----------------------------------------------------Calculating Throughput for every timestamp----------------------------
############################################################################################################################

    prev_timestamp = None
    length = 1

    for timestamp in data_rates:
        if prev_timestamp is not None:
            throughput[timestamp] = data_rates[timestamp]["data_rate"]*(1-data_rates[timestamp]["frame_losses"]/length)
            length+=1
            prev_timestamp = timestamp
        else: 
            throughput[timestamp] = data_rates[timestamp]["data_rate"]
            prev_timestamp = timestamp
            length+=1

############################################################################################################################
#----------------------------------------------------Store data regarding Throughput and rate gap in differen files---------
############################################################################################################################

    RSSI_for_visualiser = f"RSSI_file_for_visualiser.txt"
    
    with open(RSSI_for_visualiser, "w", encoding="utf-8") as RSSI_file:
            for timestamp in data_frames.keys():
                RSSI_file.write(str(timestamp) +"::"+str(data_frames[timestamp]["RSSI"])+ '\n')

    throughput_file_for_visualiser = f"throughput_file_for_visualiser.txt"
    
    with open(throughput_file_for_visualiser, "w", encoding="utf-8") as throughput_file:
            for timestamp in throughput.keys():
                throughput_file.write(str(timestamp) +"::"+str(throughput[timestamp])+ '\n')

    rate_gap_file = f"rate_gap_file.txt"

    with open(rate_gap_file, "w", encoding="utf-8") as rate_gap:
            for timestamp in rate_gaps.keys():
                rate_gap.write(str(timestamp) +"::"+str(rate_gaps[timestamp])+ '\n')

    data_rate_and_frame_loss_file = f"rates_file.txt"

    with open(data_rate_and_frame_loss_file, "w", encoding="utf-8") as ratess:
            length = 1
            for timestamp in data_rates.keys():
                ratess.write(str(timestamp) +"::"+str(data_rates[timestamp]["data_rate"])+"::"+str(data_rates[timestamp]["frame_losses"]/length)+ '\n')
                length +=1

############################################################################################################################
#----------------------------------------------------Calculate and print the throughput average----------------------------
############################################################################################################################

    frame_loss_rate = losses / total_frames
    avg_data_rate = sum(rates) / len(rates)
    av_throughput = avg_data_rate * (1 - frame_loss_rate)

    av_throughput_data = []

    av_throughput_data.append(total_frames)
    av_throughput_data.append(losses)
    av_throughput_data.append(frame_loss_rate)
    av_throughput_data.append(avg_data_rate)
    av_throughput_data.append(av_throughput)

    throughput_params = f"throughput_params.txt"

    with open(throughput_params, "w", encoding="utf-8") as params:
            params.write(str(channel_util) +"::"+str(mac_eff)+ '\n')

    return throughput_file_for_visualiser, av_throughput_data , rate_gap_file, throughput_params, data_rate_and_frame_loss_file, RSSI_for_visualiser