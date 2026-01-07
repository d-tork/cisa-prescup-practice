"""
Crack a hashed password for a known hashing algorithm and with johntheripper and a wordlist.

Challenge reference: pc2/team/round1-2-boxes-4-shells

"""
import sys
import argparse
import textwrap
from pathlib import Path, PurePath


def parse_args(args: list):
    parser = argparse.ArgumentParser(prog="PasswordCracker",
                                      description=sys.modules[__name__].__doc__)
    parser.add_argument("--you", default="ATTACK_PLATFORM", help="IP address of your attack platform")
    parser.add_argument("--wordlist", type=PurePath, default=Path("/usr/share/wordlists/rockyou.txt"), 
                        help="Path to wordlist")
    parser.add_argument("--fmt", default="raw-sha256", metavar="FORMAT", help="Hashing algorithm used")
    parser.add_argument("--tgtfile", default= "hashed_pswd.txt", metavar="TARGETFILE", 
                        help="File containing the hashed password")
    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    print(sys.argv[0])
    print(sys.modules[__name__].__doc__)

    wordlist_file = args.wordlist.name
    instruction("Copy hash to your system as a txt file", where=args.you)
    instruction(find_wordlist(filename=wordlist_file), where=args.you)
    instruction(unzip_wordlist(filepath=args.wordlist), root=True, where=args.you)
    instruction(john_the_ripper(wordlist=args.wordlist, fmt=args.fmt, tgtfile=args.tgtfile), root=True, where=args.you)
    return


def instruction(output, where: str, root: bool = False):
    """Wrap some output in a block designating the host it should be executed on."""
    prefix = f"==================== on {where} =================="
    print(prefix)
    if root:
        print("********************* (as root) ********************")
    print(output)
    suffix = "---------------------------------------------------"
    print(suffix)
    return


def find_wordlist(filename: str = "rockyou.txt") -> str:
    cmd = textwrap.dedent(f"""
    [ locate the wordlist you need ]

    find / -name *{filename}* 2>/dev/null
    """)
    return cmd


def unzip_wordlist(filepath: str, ext: str = ".gz") -> str:
    compressed_path = f"{filepath}{ext}"
    cmd = textwrap.dedent(f"""
    [unzip the result of the find command above, IAW its compresion]

    gunzip {compressed_path}
    
    tar -xf {compressed_path}
    
    unzip {compressed_path}
    """)
    return cmd

def john_the_ripper(wordlist: str, fmt: str, tgtfile: str) -> str:
    cmd = textwrap.dedent(f"""
    john --wordlist={wordlist} --format={fmt} {tgtfile}
    """)
    return cmd


if __name__ == '__main__':
    main()
