# DoublePulsar passive detector

<div>
  <!-- Stability -->
  <a href="https://nodejs.org/api/documentation.html#documentation_stability_index">
    <img src="https://img.shields.io/badge/stability-experimental-orange.svg?style=flat-square"
      alt="API stability" />
  </a>
  <!-- Standard -->
  <a href="https://img.shields.io/badge">
    <img src="https://img.shields.io/badge/Language-C-brightgreen.svg"
      alt="Python" />
  </a>
</div>
<br />

## DoublePulsar

DOUBLEPULSAR is one of NSA implants and backdoors disclosed on 2017/04/14 by a
group known as "Shadow Brokers".

The implant allows an unauthenticated, remote attacker to use SMB as a covert 
channel to execute arbitrary code. DOUBLEPULSAR uses SMB features that have
never been implemented by Microsoft, the "trans2" feature (Transaction 2
Subcommand Extension).

A specific request ("TRANS2_SESSION_SETUP" command) is sent to test whether the
target is infected or not. The backdoor's response is hidden in the MultiplexID
value returned.

- A normal system will answer with the same MultiplexId as the request (0x41).
- An infected system will answer with a MultiplexId incremented by 0x10 (0x51).

This difference is the way that the backdoor return its status code (0x10 = ok)

## Example

### Usage
```
> DoublePulsarDetector.exe

Usage: DoublePulsarDetector.exe options

    Options:
    --help/-h              : Show this message
    --list                 : List all interfaces
    --live [interface_num] : Capture packets from an interface
    --file [filename]      : Capture packets from a file

```

## Using testdata
```
> DoublePulsarDetector.exe --file ..\Data\doublepulsar-backdoor-connect-win7.pcap

18:09:52.484121 192.168.198.204:50975 -> 192.168.198.203:445   - DoublePulsar Backdoor Test
18:09:52.484150 192.168.198.203:445   -> 192.168.198.204:50975 - DoublePulsar Backdoor Response (INFECTED)
```
