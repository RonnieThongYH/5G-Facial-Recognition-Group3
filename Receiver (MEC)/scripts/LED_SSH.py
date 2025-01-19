import paramiko

# Replace these with your Raspberry Pi's IP address, username, and password.

raspberry_pi_ip = "100.67.219.182"
username = "pi"
password = "raspberry"
# Establish SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(raspberry_pi_ip, username=username, password=password)

# Raspberry Pi Python script to Turn on the LED
python_script = """
import RPi.GPIO as GPIO #import RPi.GPIO module
from time import sleep #used to create delays

GPIO.setmode(GPIO.BCM) #choose BCM mode
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT) #set GPIO 22 GPIOas output
GPIO.output(22,1) #output logic high/'1'

"""
python_script2 = """
import RPi.GPIO as GPIO #import RPi.GPIO module
from time import sleep #used to create delays

GPIO.setmode(GPIO.BCM) #choose BCM mode
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT) #set GPIO 22 GPIOas output
GPIO.output(22,0) #output logic Low/'0'

"""
while True:
    Input_value=input("Enter '1' to turn LED on or '0' to turn LED off ('Q' to quit):")

    # Exit
    if Input_value=='Q':
        break
    
    # Send the script and execute it on the Raspberry Pi
    if Input_value=='1':
        stdin, stdout, stderr = ssh.exec_command("python -c '{}'".format(python_script))
        print("LED ON!!!")
    if Input_value=='0':
        stdin, stdout, stderr = ssh.exec_command("python -c '{}'".format(python_script2))
        print("LED OFF!!!")
        
# Close the SSH connection
ssh.close()
