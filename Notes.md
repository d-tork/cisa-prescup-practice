# Notes

## Scanning

If nmap isn't available you can use netcat to scan:
```
# lower ports
nc -w 1 -zv x.x.x.x 1-1023 > ncscan.txt 2>&1
grep -v refused ncscan.txt

# or for all the ports
nc -w 1 -zv x.x.x.x 1-65535 > ncscan.txt 2>&1
```

## Crack a password hash

Use john-the-ripper (`john`), passing a wordlist as a txt and the hashing algorithm, then the file containing the hash. 

## Connecting

When SSH is filtered and you don't have a route directly from your box to the target, but you can go through an intermediate one, create a netcat relay to pivot.

## Common Exploits

If FTP (port 21) is open, use Filezilla to get a file.

Cracking a remote service password (ssh, smb, redis, rdp, postgres, sql, ftp, etc.) given a username and password list: use xHydra.

## Priv escalation

Standard practice is to check for vulnerable versions of sudo, and list sudo permissions for a user
```bash
sudo -V

sudo -l
```

## Reverse engineering / binary analysis

To analyze a binary to find a list of dynamically-linked symbols, use
```bash
nm -D mybinary
```

To run the GNU debugger: 
```bash
chmod +x mybinary
gdb ./mybinary
```
Then add a breakpoint at the function identified from `nm` (because `AES_ige_encrypt` is the only thing having to do with the question, about encryption)
```
(gdb) b AES_ige_encrypt
# answer yes to the prompt

# then run the program
(gdb) r

# print registers
(gdb) info r

# examine a buffer at a location (in this case, `rsi` leads to `0x5555555bc7e0`)
(gdb) x/32bc 0x5555555bc7e0

# run the program until the next return occurs
(gdb) fin
```

# Defense

## How to spot a SQL injection

Collect a pcap during the time you think the injection took place, open it in Wireshark, and search the **packet details** for a **string** that matches common SQL injection patterns, such as `1=1`. Now you have the IP of the attacker. 

## Find a brute force attacker

In Wireshark looking at packets sent to your web server (`ip.dst == x.x.x.x`), look for multiple hits on the login page per second, in rapid succession. That's your attacker. 

## Identify what was exfiltrated from a website

In wireshark, go to File > Export Objects > HTTP and choose the content type (in this case we were **told** it was a sql database, so choose `application/x-sqlite3`). You can download the file from there. 
