from netmiko import ConnectHandler
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import os
from rich.console import Console
import typer
from typing import Optional


def get_credentials():
    # Get username and password from user
    username = input("Please enter your username: ")
    password = getpass("Enter your password: ")

    return (username, password)


def print_banner():
    print("-" * 40)
    print("Config collector tool - v1.3")
    print("For support please contact Suhaib Saeed")
    print("-" * 40)


def get_time():
    # Get the current time - This will be used in the file name
    now = datetime.datetime.now()
    # Structure the time in Date-Month-Year with Hours.Minutes
    time_now = now.strftime("%d-%m-%y@%H.%M")

    return time_now


def get_devices_file(device_file):
    with open(device_file) as f:

        devices = f.read().splitlines()
        # Remove whitespaces from lines and blank lines
        devices = [i.strip() for i in devices]
        devices = [x for x in devices if x]

        return devices


def get_commands(commands_file):
    with open(commands_file) as f:
        commands = f.read().splitlines()
        # Remove whitespaces from lines and blank lines
        commands = [i.strip() for i in commands]
        commands = [x for x in commands if x]

        return commands


def ssh_command(device, show_commands, time_now, creds):
    """
    Connect to the device via Netmiko and execute commands in the list
    :param device: Netmiko device hostname
    :param show_commands: Show commands to send to the device
    :return: Output of the command from the device
    """

    console = Console(log_path=False)
    username = creds[0]
    password = creds[1]

    # Dictionary that hold the device details
    device_dict = {
        "host": device,
        "username": username,
        "password": password,
        "device_type": "autodetect",
        "secret": password,
        "conn_timeout": 45,
    }

    # Establish SSH connection to the network device using **kwargs to pull in details from dictionary
    net_connection = ConnectHandler(**device_dict)
    print("*" * 50)
    console.log(f"[green]Successfully connected to {device}[/green]")
    print("*" * 50)
    # Go into enable mode - fixes issue of show run on IOS being missed out
    net_connection.enable()

    # Find prompt - Gives us hostname which will be used later in writing the name of file
    hostname = (
        net_connection.find_prompt().rstrip(">").lstrip(f"{username}@").rstrip("#")
    )
    # Create directory path we're writing files to - We want everything in output folder
    complete_name = os.path.join("output", hostname)
    # Open new file for writing based on hostname and the current time
    new_file = open(f"{complete_name}-{time_now}.txt", "a")

    # Loop through commands in the text file
    for command in show_commands:

        # Increase timeout show logging as it has lots of output
        if "show logging" in command:
            output = net_connection.send_command_timing(command)
        # Send the command to the device
        else:
            output = net_connection.send_command(command)
        # Stops command and output being on the same line
        new_file.write(command + "\n" + "*" * 20 + "\n")
        # Write command output to the file
        new_file.write(output)
        print("-" * 75)
        # Print confirmation to the user
        console.log(
            f"[cyan]{command} was successfully collected from {hostname}[/cyan]"
        )
        print("-" * 75)
        new_file.write("\n" + "=" * 80 + "\n")

    # Close the file
    new_file.close()


def main(
    single_device: Optional[str] = typer.Argument(
        None, help="Optional: Single device to connect to, used instead of devices.txt"
    )
):
    """
    This tool uses the devices listed in devices.txt and commands in commands.txt, connects to each device and executes the commands.
    The results are then written to a file per device in the output folder. Or run with a single device by specifying it.
    """
    print_banner()
    time = get_time()
    commands = get_commands("commands.txt")
    credentials = get_credentials()

    # Check if user has passed in a single device to connect to, instead of using devices.txt
    if single_device is None:
        devices = get_devices_file("devices.txt")
    else:
        devices = [single_device]

    # Specify how big the thread pool is
    max_threads = 20
    # Create instance of ThreadPoolExecutor object and pass in max_thread no
    pool = ThreadPoolExecutor(max_threads)

    # Loop through the devices
    for device in devices:
        # Start 20 child threads and submit them into the thread pool
        future = pool.submit(
            ssh_command, device, commands, time, credentials
        )  # Pass in ssh_command, device and command args


if __name__ == "__main__":
    typer.run(main)
