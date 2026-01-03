"""
Creates the commands for a netcat relay to SSH into a target via pivot machine.

"""
import sys
import argparse


def parse_args(args: list):
    parser = argparse.ArgumentParser(prog="NetcatRelayPivot",
                                      description="Create the commands for a netcat relay to pivot.")
    parser.add_argument("--you", required=True, help="IP address of your attack platform")
    parser.add_argument("--pivot", required=True, help="IP address of the pivot box")
    parser.add_argument("--tgt", required=True, metavar="TARGET", help="IP address of the target")
    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    label(start_nc_relay, host=args.you)
    return


def label(func, host: str, *args, **kwargs):
    """Wrap some output in a block designating the host it should be executed on."""
    prefix = f"==================== on {host} =================="
    print(prefix)
    print(func(*args, **kwargs))
    suffix = "==================================================="
    print(suffix)
    return


def start_nc_relay(local_port: int = 2222, remote_port: int = 22222) -> str:
    device_name = "backpipe"
    device_type = "p"
    cmd = f"""
    mknod {device_name} {device_type}
    nc -lvp {local_port} 0<{device_name} | nc -lvp {remote_port} | tee {device_name}
    """
    return cmd


if __name__ == '__main__':
    main()
