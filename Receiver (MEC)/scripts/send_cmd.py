import paramiko

# Replace these with your Raspberry Pi's IP address, username, and password.

raspberry_pi_ip = "100.70.118.250"
username = "pi"
password = "raspberry"
# Establish SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(raspberry_pi_ip, username=username, password=password)


# Function to turn the LED on
def turn_led_on(ssh):
    python_script = """
import RPi.GPIO as GPIO #import RPi.GPIO module
from time import sleep #used to create delays

GPIO.setmode(GPIO.BCM) #choose BCM mode
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT) #set GPIO 22 GPIOas output
GPIO.output(22,1) #output logic high/'1'

"""
    stdin, stdout, stderr = ssh.exec_command(f"python3 -c '{python_script}'")
    print("LED ON!!!")

# Function to turn the LED off
def turn_led_off(ssh):
    python_script2 = """
import RPi.GPIO as GPIO #import RPi.GPIO module
from time import sleep #used to create delays

GPIO.setmode(GPIO.BCM) #choose BCM mode
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT) #set GPIO 22 GPIOas output
GPIO.output(22,0) #output logic Low/'0'

"""
    stdin, stdout, stderr = ssh.exec_command(f"python3 -c '{python_script2}'")
    print("LED OFF!!!")
# Close the SSH connection
ssh.close()
