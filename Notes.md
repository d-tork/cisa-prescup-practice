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

Cracking a remote service password (ssh, smb, redis, rdp, postgres, sql, ftp, etc.) given a password list: use xHydra.

## Priv escalation

Standard practice is to check for vulnerable versions of sudo, and list sudo permissions for a user
```bash
sudo -V

sudo -l
```
