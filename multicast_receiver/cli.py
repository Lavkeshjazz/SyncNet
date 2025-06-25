import argparse
from receiver import join_multicast, listen

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multicast File Receiver")
    parser.add_argument("--ip", required=True, help="Multicast IP to join")
    args = parser.parse_args()

    sock = join_multicast(args.ip)
    listen(sock)
