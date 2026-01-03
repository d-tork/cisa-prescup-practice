"""
Crack a hashed password for a known hashing algorithm and with johntheripper and a wordlist.

"""
import sys
import argparse
import textwrap


def parse_args(args: list):
    parser = argparse.ArgumentParser(prog="PasswordCracker",
                                      description=sys.modules[__name__].__doc__)
    parser.add_argument("--you", default="ATTACK_PLATFORM", help="IP address of your attack platform")
    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    instruction("Copy hash to your system as a txt file", where=args.you)
    instruction(find_wordlist(), where=args.you)
    instruction(unzip_wordlist(), root=True, where=args.you)
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


def unzip_wordlist(filepath: str = "/usr/share/wordlists/rockyou.txt.gz") -> str:
    cmd = textwrap.dedent(f"""
    [unzip the result of the find command above, IAW its compresion]

    gunzip {filepath}
    
    tar -xf {filepath}
    
    unzip {filepath}
    """)
    return cmd


if __name__ == '__main__':
    main()
