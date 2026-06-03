/*
 * vm_artifacts.yar
 * ================
 * YARA rules targeting VirtualBox and VMware artefacts, including
 * .vbox XML configuration markers and Guest Additions indicators.
 *
 * Author : KALINALYSIS project
 * Created: 2026-06-02
 * License: Apache-2.0
 */

rule VBox_Config_XML
{
    meta:
        description = "Detects VirtualBox machine configuration files (.vbox)"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "virtualbox, vbox, config, vm"
        severity    = "info"

    strings:
        $xml_header  = "<?xml version=\"1.0\""
        $vbox_tag    = "<VirtualBox xmlns="
        $machine_tag = "<Machine uuid="
        $os_type     = "OSType=\""

    condition:
        $xml_header and $vbox_tag and $machine_tag and $os_type
}

rule VBox_Snapshot_XML
{
    meta:
        description = "Detects VirtualBox snapshot descriptor files (.vbox-prev or snapshot XML)"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "virtualbox, snapshot, vm"
        severity    = "info"

    strings:
        $snap  = "<Snapshot uuid="
        $vbox  = "<VirtualBox xmlns="
        $state = "stateFile="

    condition:
        $vbox and $snap and $state
}

rule VBox_GuestAdditions_Binary
{
    meta:
        description = "Detects VirtualBox Guest Additions binaries by embedded string markers"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "virtualbox, guest-additions, binary"
        severity    = "info"

    strings:
        $ga1 = "VBoxGuestAdditions" ascii wide
        $ga2 = "Oracle VM VirtualBox Guest Additions" ascii wide
        $ga3 = "VBoxService" ascii wide
        $ga4 = "VBoxClient" ascii wide

    condition:
        2 of them
}

rule VMware_VMDK_Header
{
    meta:
        description = "Detects VMware VMDK virtual disk image headers"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "vmware, vmdk, disk-image"
        severity    = "info"

    strings:
        // VMDK sparse extent magic
        $sparse_magic = { 4B 44 4D 56 }
        // VMDK descriptor text marker
        $desc = "# Disk DescriptorFile" ascii
        $type = "createType=\"" ascii

    condition:
        $sparse_magic at 0 or ($desc and $type)
}

rule VMware_VMX_Config
{
    meta:
        description = "Detects VMware .vmx configuration files"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "vmware, vmx, config"
        severity    = "info"

    strings:
        $vmx1 = ".encoding = \"" ascii
        $vmx2 = "guestOS = \"" ascii
        $vmx3 = "memSize = \"" ascii
        $vmx4 = "nvram = \"" ascii

    condition:
        3 of them
}

rule KaliLinux_VBox_OVA_Manifest
{
    meta:
        description = "Detects Kali Linux VirtualBox OVA/OVF manifest files"
        author      = "KALINALYSIS"
        date        = "2026-06-02"
        tags        = "kali, virtualbox, ova, ovf"
        severity    = "info"

    strings:
        $ovf1 = "<ovf:Envelope" ascii
        $ovf2 = "kali" nocase ascii
        $ovf3 = "VirtualBox" ascii
        $os_id = "101" ascii  // Debian-based OS identifier in OVF

    condition:
        $ovf1 and $ovf2 and ($ovf3 or $os_id)
}
