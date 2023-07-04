import paramiko
import sys

def ssh_conn(host, user, password):
    
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password= passwd )
    
        cmd = '/usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -n -f 30 -r 1280x720" > -o "/usr/local/lib/mjpg-streamer/output_http.so -p 8085 -w /usr/local/share/mjpg-streamer/www"'
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(cmd)
        print(ssh_stdout.read().decode())
        client.close()
    except Exception as err:
        print(str(err))

def ssh_terminal(host, user, password):
    
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password= passwd )
    
        while True:
            try:
                cmd = '/usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -n -f 30 -r 1280x720" > -o "/usr/local/lib/mjpg-streamer/output_http.so -p 8085 -w /usr/local/share/mjpg-streamer/www"'
                if cmd == 'exit': break
                ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(cmd)
                print(ssh_stdout.read().decode())
            except KeyboardInterrupt:
                break
            client.close()
    except Exception as err:
        print(str(err))    

host = '10.20.1.1'
user = 'utebot'
passwd = 'ddm-utebot'

ssh_conn(host, user, passwd)
ssh_terminal(host, user, passwd)
