import time
import csv
import os
import psutil
import requests
import subprocess
import speedtest
import matplotlib.pyplot as plt



def get_user_isp(): #Get user's ISP information
    
    try:
        isprequest = requests.get("https://ipinfo.io")
        isp = isprequest.json()
        return isp.get("org", "Unknown ISP")
    except Exception as e:
        print(f"Error in getting ISP information: {e}")
        return "Unknown ISP"

def get_connection_method():  #Find user network connection
   
    method = psutil.net_if_addrs()
    
    for interface in method.keys():
        if 'Wi-Fi' in interface or 'wlan' in interface.lower():
            return 'Wi-Fi'
        elif '4g' in interface.lower() or 'lte' in interface.lower():
            return '4G'
        elif '5g' in interface.lower():
            return '5G'
        elif 'mobile' in interface.lower():
            return 'Mobile Data'
        elif 'hotspot' in interface.lower():
            return 'Hotspot'
        elif 'tether' in interface.lower():
            return 'Tethering'
        elif 'Ethernet' in interface or 'eth' in interface.lower():
            return 'Ethernet'
    
    return 'Unknown'

def tracert(servertest): #Traceroute to test server
    
    result = subprocess.run(["tracert", servertest], capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout.splitlines()
    else:
        return [f"Error: {result.stderr}"]

def suitable_uses(download_speed, upload_speed): #Determine and print suitable uses based on download and upload speeds
    
    print("\nSuitable Uses for This Speed Test:")
    
    if download_speed >= 25:
        print("Download speed suitable for 4K video streaming and online gaming.")
    elif download_speed >= 10:
        print("Download speed suitable for HD video streaming and video conferencing.")
    elif download_speed >= 5:
        print("Download speed suitable for standard definition video and browsing social media.")
    else:
        print("Download speed suitable for minimum use.")
    
    if upload_speed >= 5:
        print("Upload speed suitable for live streaming and uploading large files.")
    elif upload_speed >= 3:
        print("Upload speed suitable for video conferencing and sharing content on social media.")
    else:
        print("Upload speed suitable for minimum use.")

def plot_results(results): #Plot download speed and upload speed, ping, and test duration per iteration
    
    iterations = list(range(1, len(results) + 1))
    download_speeds = [result['download_speed'] for result in results]
    upload_speeds = [result['upload_speed'] for result in results]
    pings = [result['ping'] for result in results]
    test_durations = [result['test_duration'] for result in results]
    
    
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(iterations, download_speeds, marker='o', label='Download Speed (Mbps)', color='blue')
    plt.plot(iterations, upload_speeds, marker='o', label='Upload Speed (Mbps)', color='orange')
    plt.title('Download and Upload Speeds Over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Speed (Mbps)')
    plt.xticks(iterations)
    plt.grid()
    plt.legend()

    
    plt.subplot(3, 1, 2)
    plt.plot(iterations, pings, marker='o', color='green')
    plt.title('Ping Over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Ping (ms)')
    plt.xticks(iterations)
    plt.grid()

    
    plt.subplot(3, 1, 3)
    plt.plot(iterations, test_durations, marker='o', color='red')
    plt.title('Test Duration Over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Duration (s)')
    plt.xticks(iterations)
    plt.grid()

    plt.tight_layout()
    plt.show()
 
    
def final_result(results): #Append all result to CSV file

    file_exists = os.path.isfile('speedtestdata.csv')

    with open('speedtestdata.csv', mode='a', newline='') as file:
        appending = csv.writer(file)
        
        if not file_exists:
            appending.writerow(['Speed Test Server',
                                'Speed Test IP Server', 
                                'Country', 
                                'Download Speed (Mbps)', 
                                'Upload Speed (Mbps)', 
                                'Ping (ms)', 
                                'Server ISP', 
                                'User ISP', 
                                'Connection Method', 
                                'Test Duration (s)'])

        for result in results:
            appending.writerow([result['Speed Test Server'], 
                                result['Speed Test IP Server'], 
                                result['country'], 
                                result['download_speed'], 
                                result['upload_speed'], 
                                result['ping'], 
                                result['Server ISP'], 
                                result['User ISP'], 
                                result['Connection Method'], 
                                result['test_duration']])

def speed_test(iterations=1):    #Perform the speed test

    testvalue = speedtest.Speedtest()
    print("Finding the best server...")
    server_info = testvalue.get_best_server()

    results = []
    connection_method = get_connection_method()
    user_isp = get_user_isp()
    server_isp = server_info['sponsor']
    ip_address = server_info['host'].split(':')[0]

    for i in range(iterations):
        try:
            print(f"\nIteration {i + 1} of {iterations}:")
            start_time = time.time()

            ping = server_info['latency']
            download_speed = testvalue.download() / 1_000_000  # Convert to Mbps
            upload_speed = testvalue.upload() / 1_000_000  # Convert to Mbps

            traceroute_hops = tracert(ip_address)
            test_duration = time.time() - start_time

            results.append({
                'Speed Test Server': server_info['name'],
                'Speed Test IP Server': ip_address,
                'country': server_info['country'],
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'ping': ping,
                'Server ISP': server_isp,
                'User ISP': user_isp,
                'Connection Method': connection_method,
                'test_duration': test_duration,
                'traceroute': traceroute_hops,
            })

           
            print(f"Download Speed: {download_speed:.2f} Mbps")
            print(f"Upload Speed: {upload_speed:.2f} Mbps")
            print(f"Ping: {ping:.2f} ms")
            print(f"Server ISP: {server_isp}")
            print(f"User ISP: {user_isp}")
            print(f"Connection Method: {connection_method}")
            print(f"Test Duration: {test_duration:.2f} seconds")

            
            suitable_uses(download_speed, upload_speed)

            
            print("\nTraceroute:")
            for hop in traceroute_hops:
                print(hop)

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(2)


    final_result(results)
    plot_results(results)

if __name__ == "__main__":
    speed_test(iterations=3)
