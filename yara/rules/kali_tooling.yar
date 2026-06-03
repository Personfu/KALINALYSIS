/*
 * kali_tooling.yar
 * ================
 * YARA rules targeting string/byte signatures commonly associated with
 * Kali Linux tools found in files, memory dumps, or filesystem artefacts.
 *
 * Author : KALINALYSIS project
 * Created: 2026-06-02
 * License: Apache-2.0
 */

rule KaliLinux_Nmap_XML_Output
{
    meta:
        description = "Detects Nmap XML scan output files"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, nmap, recon, xml"
        severity    = "info"

    strings:
        $xml_header = "<?xml version=\"1.0\""
        $nmaprun     = "<nmaprun scanner=\"nmap\""
        $host_tag    = "<host starttime="
        $port_tag    = "<port protocol="

    condition:
        $xml_header and $nmaprun and ($host_tag or $port_tag)
}

rule KaliLinux_Metasploit_Stager_Reverse_TCP
{
    meta:
        description = "Detects common Metasploit reverse_tcp stager byte patterns"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, metasploit, stager, payload"
        severity    = "high"
        reference   = "https://github.com/rapid7/metasploit-framework"

    strings:
        // msfvenom reverse_tcp shellcode prologue patterns (x86)
        $s1 = { FC E8 89 00 00 00 60 89 E5 31 D2 64 8B 52 30 }
        // EXITFUNC=thread marker
        $s2 = { 00 00 00 00 00 00 FF D5 87 DA FF D5 3C 06 }
        // LPORT/LHOST push pattern (partial — context-dependent)
        $s3 = "EXITFUNC=thread" nocase

    condition:
        any of them
}

rule KaliLinux_Hydra_Bruteforce_Log
{
    meta:
        description = "Detects Hydra brute-force tool output files"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, hydra, brute-force, credentials"
        severity    = "medium"

    strings:
        $h1 = "Hydra v" ascii
        $h2 = "[DATA] attacking" ascii
        $h3 = "[STATUS] attack finished" ascii
        $h4 = "1 of 1 target successfully completed" ascii

    condition:
        2 of them
}

rule KaliLinux_SQLMap_Output
{
    meta:
        description = "Detects sqlmap output logs and dump files"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, sqlmap, sql-injection, web"
        severity    = "medium"

    strings:
        $s1 = "sqlmap identified the following injection point" ascii
        $s2 = "sqlmap resumed the following injection point" ascii
        $s3 = "[INFO] testing '" ascii
        $s4 = "back-end DBMS:" ascii

    condition:
        2 of them
}

rule KaliLinux_John_Cracked_Passwords
{
    meta:
        description = "Detects John the Ripper cracked password output"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, john, password-cracking"
        severity    = "high"

    strings:
        $j1 = "Loaded " ascii
        $j2 = " password hashes with " ascii
        $j3 = "Press 'q' or Ctrl-C to abort" ascii
        $j4 = "Session completed" ascii
        $j5 = "guesses:" ascii

    condition:
        3 of them
}

rule KaliLinux_Dirb_Wordlist_Scan
{
    meta:
        description = "Detects dirb / gobuster directory brute-force output"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, dirb, gobuster, web, enumeration"
        severity    = "low"

    strings:
        $d1 = "DIRB v" ascii
        $d2 = "---- Scanning URL:" ascii
        $d3 = "==> DIRECTORY:" ascii
        $g1 = "Gobuster" ascii
        $g2 = "Progress: " ascii
        $g3 = "/Status: " ascii

    condition:
        (2 of ($d*)) or (2 of ($g*))
}
