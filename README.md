<p align="center"><img width=550 alt="HTTP-Shell" src="https://github.com/JoelGMSec/HTTP-Shell/blob/main/HTTP-Shell.png"></p>

# HTTP-Shell
**HTTP-Shell** is Multiplatform Reverse Shell. This tool helps you to obtain a shell-like interface on a reverse connection over HTTP. Unlike other reverse shells, the main goal of the tool is to use it in conjunction with Microsoft Dev Tunnels, in order to get a connection as close as possible to a legitimate one.

This shell is not fully interactive, but displays any errors on screen (both Windows and Linux), is capable of uploading and downloading files, has command history, terminal cleanup (even with CTRL+L), automatic reconnection and movement between directories.


# Requirements
- Python 3 for Server
- Install requirements.txt
- Bash for Linux Client
- PowerShell 4.0 or greater for Windows Client


# Download
It is recommended to clone the complete repository or download the zip file.
You can do this by running the following command:
```
git clone https://github.com/JoelGMSec/HTTP-Shell
```


# Usage
```
# Server

  _   _ _____ _____ ____      ____  _          _ _ 
 | | | |_   _|_   _|  _ \    / ___|| |__   ___| | |
 | |_| | | |   | | | |_) |___\___ \| "_ \ / _ \ | |
 |  _  | | |   | | |  __/_____|__) | | | |  __/ | |
 |_| |_| |_|   |_| |_|       |____/|_| |_|\___|_|_|
                                               
  ---------------- by @JoelGMSec -----------------

[!] Usage: HTTP-Server.py [PORT]


# Linux CLI

[!] Usage: ./HTTP-Client.sh -c [HOST:PORT] -s [SLEEP] (optional)


# Windows CLI

[!] Usage: .\HTTP-Client.ps1 -c [HOST:PORT] -s [SLEEP] (optional)

```

### The detailed guide of use can be found at the following link:

https://darkbyte.net/obteniendo-shells-con-microsoft-dev-tunnels


# License
This project is licensed under the GNU 3.0 license - see the LICENSE file for more details.


# Credits and Acknowledgments
This tool has been created and designed from scratch by Joel Gámez Molina (@JoelGMSec).


# Contact
This software does not offer any kind of guarantee. Its use is exclusive for educational environments and / or security audits with the corresponding consent of the client. I am not responsible for its misuse or for any possible damage caused by it.

For more information, you can find me on Twitter as [@JoelGMSec](https://twitter.com/JoelGMSec) and on my blog [darkbyte.net](https://darkbyte.net).


# Support
You can support my work buying me a coffee:

[<img width=250 alt="buymeacoffe" src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png">](https://www.buymeacoffee.com/joelgmsec)
