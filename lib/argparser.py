import argparse as ap
import ipaddress as ipa

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ap.ArgumentTypeError('Boolean value expected.')

def ipv4_check(v):
    try:
        ipa.ip_address(v)
        return v
    except Exception as e:
        print(e)


class InputArguments:
    def __init__(self):
        self.parser = ap.ArgumentParser()
        self.parser.add_argument('--host', type=ipv4_check, help='broker host address')
        self.parser.add_argument('-p', type=int, nargs='?', const=8883, default=8883,
                                 help='broker port number')
        #self.parser.add_argument('--refr', type=float, help='refresh rate')

        self.parser.add_argument("--ct", type=str2bool, nargs='?',
                            const=True, help="Activate cputemp")
        self.parser.add_argument("--cl", type=str2bool, nargs='?',
                                 const=True, help="Activate cpuload")
        self.parser.add_argument("--memo", type=str2bool, nargs='?',
                                 const=True, help="Activate memories")

    def prepare(self):
        return 0
