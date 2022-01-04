from netmiko import ConnectHandler
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import os

print('-' * 31)
print("Config collector tool - v1.3 Beta")
print("For support please contact saeed.suhaib@gmail.com")
print('-' * 31)
# Get username and password from user
username = input("Please enter your username: ")
password = getpass()

# Open both files which have list of devices and commands to send to them
with open("devices.txt") as fp:
    devices = fp.read().splitlines()

with open("commands.txt") as f:
    commands = f.read().splitlines()

# Get the current time - This will be used in the file name
now = datetime.datetime.now()
# Structure the time in Date-Month-Year with Hours.Minutes
time_now = now.strftime("%d-%m-%y@%H.%M")


def ssh_command(device, show_commands):
    """
    Connect to the device via Netmiko and execute commands in the list
    :param device: Netmiko device hostname
    :param show_commands: Show commands to send to the device
    :return: Output of the command from the device
    """

    # Dictionary that hold the device details
    juniper_device = {
        'host': device,
        'username': username,
        'password': password,
        'device_type': 'juniper',
        'secret': password,
        'conn_timeout': 45
        }

    # Establish SSH connection to the network device using **kwargs to pull in details from dictionary
    net_connection = ConnectHandler(**juniper_device)
    print("*" * 80)
    print(f"Successfully connected to {device}")
    print("*" * 80)
    # Go into enable mode - fixes issue of show run on IOS being missed out
    net_connection.enable()

    # Loop through commands in the text file
    for i in range(len(show_commands)):
        # Find prompt - Gives us hostname which will be used later in writing the name of file
        hostname = net_connection.find_prompt().rstrip('>').lstrip('root@')
        # Create directory path we're writing files to - We want everything in output folder
        complete_name = os.path.join('output', hostname)

        # Open new file for writing based on hostname and the current time
        new_file = open(f"{complete_name}-{time_now}.txt", "a")
        # Increase timeout show logging as it has lots of output
        if 'show logging' in commands[i]:
            output = net_connection.send_command_timing(commands[i])
        # Deal with additional prompting on IOS devices
        elif commands[i].lower() == 'copy run start':
            output = net_connection.send_command_timing(commands[i])
            output += net_connection.send_command_timing('\n')
        # Send the command to the device
        else:
            output = net_connection.send_command(commands[i])
        # Stops command and output being on the same line
        new_file.write(commands[i] + "\n")
        # Write command output to the file
        new_file.write(output)
        print('-' * 50)
        # Print confirmation to the user
        print(f"{commands[i]} was successfully collected from {hostname}")
        print('-' * 50)
        new_file.write('\n')
        # To separate each command's output
        new_file.write('=' * 80)
        new_file.write('\n')
        # Close the file
        new_file.close()


def main():
    """
    Use threading and Netmiko to connect to each device using concurrent futures. Execute commands on each device.
    """

    # Specify how big the thread pool is
    max_threads = 8
    # Create instance of ThreadPoolExecutor object and pass in max_thread no
    pool = ThreadPoolExecutor(max_threads)

    future_list = []

    # Loop through the devices
    for device in devices:
        # Start 8 child threads and submit them into the thread pool
        future = pool.submit(ssh_command, device, commands) # Pass in ssh_command, device and command args
        # Append each thread to the list
        future_list.append(future)

    # Instead of waiting for all pending threads to finish - process them as they come in
    for future in as_completed(future_list): # Pass in list created above into as_completed function
        # Print result
        print("Result" + future.result())


if __name__ == '__main__':
   main()
