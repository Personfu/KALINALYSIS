/*
 * offensive_indicators.yar
 * ========================
 * Generic offensive-security indicators: reverse shell patterns,
 * encoded payloads, and common red-team tooling artefacts.
 *
 * Author : KALINALYSIS project
 * Created: 2026-06-02
 * License: Apache-2.0
 */

rule OffSec_Bash_Reverse_Shell
{
    meta:
        description = "Detects common bash reverse shell one-liner patterns"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, reverse-shell, bash"
        severity    = "high"

    strings:
        $s1 = "bash -i >& /dev/tcp/" nocase
        $s2 = "bash -c 'bash -i" nocase
        $s3 = "/dev/tcp/" ascii
        $s4 = "0>&1" ascii

    condition:
        ($s1 or $s2) and ($s3 or $s4)
}

rule OffSec_Python_Reverse_Shell
{
    meta:
        description = "Detects Python-based reverse shell snippets"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, reverse-shell, python"
        severity    = "high"

    strings:
        $p1 = "import socket,subprocess,os" ascii
        $p2 = "s=socket.socket(socket.AF_INET" ascii
        $p3 = "os.dup2(s.fileno(),0)" ascii
        $p4 = "subprocess.call([\"/bin/sh\"])" ascii

    condition:
        2 of them
}

rule OffSec_Netcat_Backdoor
{
    meta:
        description = "Detects netcat listener / backdoor commands"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, netcat, backdoor"
        severity    = "high"

    strings:
        $nc1 = "nc -lvp" nocase
        $nc2 = "nc -nlvp" nocase
        $nc3 = "nc -e /bin/bash" nocase
        $nc4 = "nc -e /bin/sh" nocase
        $nc5 = "ncat --exec" nocase

    condition:
        any of them
}

rule OffSec_Base64_Encoded_Payload
{
    meta:
        description = "Detects base64-encoded payloads piped to bash/sh/python"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, obfuscation, base64, payload"
        severity    = "medium"

    strings:
        $pipe_bash   = "base64 -d | bash" nocase
        $pipe_sh     = "base64 -d | sh" nocase
        $pipe_python = "base64 -d | python" nocase
        $eval_b64    = "eval(base64.b64decode(" ascii
        $echo_pipe   = "echo " ascii
        $b64_flag    = "| base64 --decode" nocase

    condition:
        ($pipe_bash or $pipe_sh or $pipe_python or $eval_b64) or
        ($echo_pipe and $b64_flag)
}

rule OffSec_PowerShell_Encoded_Command
{
    meta:
        description = "Detects PowerShell encoded command execution (-EncodedCommand)"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, powershell, obfuscation, windows"
        severity    = "high"

    strings:
        $enc1 = "-EncodedCommand" nocase
        $enc2 = "-enc " nocase
        $enc3 = "-e " nocase
        $ps1  = "powershell" nocase
        $ps2  = "pwsh" nocase

    condition:
        ($ps1 or $ps2) and ($enc1 or $enc2 or $enc3)
}

rule OffSec_Meterpreter_HTTP_Stager
{
    meta:
        description = "Detects Meterpreter HTTP/HTTPS stager indicators"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, metasploit, meterpreter, stager"
        severity    = "high"
        reference   = "https://github.com/rapid7/metasploit-framework"

    strings:
        $ua  = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)" ascii
        $hdr = "x-token:" ascii
        $uri = "/initialsession" ascii
        $b4  = { 4D 5A 90 00 03 00 00 00 }  // PE MZ header (staged download)

    condition:
        ($ua and $hdr) or ($uri and $ua) or $b4
}

rule OffSec_Web_Shell_Generic
{
    meta:
        description = "Detects common PHP/ASP web shell indicators"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "offsec, webshell, php, asp"
        severity    = "high"

    strings:
        $php1 = "<?php eval(" nocase
        $php2 = "<?php system(" nocase
        $php3 = "<?php passthru(" nocase
        $php4 = "<?php exec(" nocase
        $php5 = "base64_decode($_" nocase
        $asp1 = "<%eval request(" nocase
        $asp2 = "<%execute(request(" nocase

    condition:
        any of them
}
