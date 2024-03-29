import asyncio
import datetime
import os
from getpass import getpass
# Import relevant driver
#from scrapli.driver.core import AsyncIOSXEDriver
#from scrapli.driver.core import AsyncNXOSDriver
from scrapli.driver.core import AsyncJunosDriver

username = input("Please enter your username: ")
password = getpass()

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

# Create co-routine which can be suspended and resumed
async def gather_commands(device, commands, time_now):
    
    net_device = {
     "host": device,
     "auth_username": username,
     "auth_password": password,
     "auth_strict_key": False,
     "transport": "asyncssh",
    }
    
    # Create object passing in device details
    connection = AsyncNXOSDriver(**net_device)
    
    # Do this everytime we have IO operation
    # Open connection
    await connection.open()
    # Store result of prompt
    hostname = await connection.get_prompt()
    # output/hostname
    complete_name = os.path.join('output', hostname)

    new_file = open(f"{complete_name}-{time_now}.txt", "a")

    # Send show version to device and store in variable
    sh_result = await connection.send_commands(commands)
    # Close connection
    await connection.close()

    for i in range(len(sh_result)):
        # Write command and output to file
        new_file.write(f"{commands[i]}\n")
        new_file.write(f"{sh_result[i].result}\n")
        new_file.write(f"{'=' * 80}\n")
    new_file.close()

    return complete_name

# Create main co-routine
async def main():
    
    # Call function to get list of devices and commands from external txt file
    devices = get_devices_file("device_list.txt")

    commands = get_commands("commands.txt")

    time_nw = get_time()

    # List comprehension calling function/coroutine above
    coroutines = [gather_commands(device, commands, time_nw) for device in devices]
    # Allows us to group together tasks
    results = await asyncio.gather(*coroutines)

    # Loop through tasks and print
    for result in results:
        result = result.split('/')[1].strip('#')
        print(f"Commands from {result} were successfully collected")


# Execute all of above - Pass in main coroutine
# Create event loop and run
asyncio.run(main())
