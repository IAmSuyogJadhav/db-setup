import argparse
import subprocess
import shlex
import os
import signal
from sys import exit, stdout
import re
import time

# Some parameters
NODE_SCRIPT = os.path.join(os.path.abspath(os.path.curdir), 'start_elasticsearch.py')  # Path to the node script
PORT_DEFAULT = 55781
# DIE_AFTER_SECONDS_DEFAULT = 20 * 60
NODES_DEFAULT = 3
K_DEFAULT = 10
MASTER_IP = 'compute-3-12'
DB_SETUP_PATH = '/home/sja082/db-assignment/db-setup/'


pat = re.compile('(\d+)')

def arg_parser():
    parser = argparse.ArgumentParser(prog="Main script", description="main script responsible for launching the elasticsearch database cluster")

    parser.add_argument("-n", "--n-nodes", type=int, default=NODES_DEFAULT,
        help="total number of nodes, default %d" % NODES_DEFAULT
    )

    parser.add_argument("-p", "--port", type=int, default=PORT_DEFAULT,
            help="port number to use, default %d" % PORT_DEFAULT
    )

    # parser.add_argument("-d", "--die-after-seconds", type=float,
    #         default=DIE_AFTER_SECONDS_DEFAULT,
    #         help="kill server after so many seconds have elapsed, " +
    #             "in case we forget or fail to kill it, " +
    #             "default %d (%d minutes)" % (DIE_AFTER_SECONDS_DEFAULT, DIE_AFTER_SECONDS_DEFAULT/60)
    # )

    return parser


class GracefulKiller():
    def __init__(self, pids):
        self.pids = pids
        self.exit_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        for pid in self.pids:
            os.kill(pid, signal.SIGKILL)
        self.exit_now = True


def generate_hosts(num_nodes, port):
    p1 = subprocess.Popen(shlex.split("rocks list host"), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split("grep compute"), stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(shlex.split('cut -d" " -f1'), stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(shlex.split("sed 's/.$//'"), stdin=p3.stdout, stdout=subprocess.PIPE)
    p5 = subprocess.Popen(shlex.split('shuf'), stdin=p4.stdout, stdout=subprocess.PIPE)
    p6 = subprocess.Popen(shlex.split(f'head -n {num_nodes}'), stdin=p5.stdout, stdout=subprocess.PIPE)
    (output, error) = p6.communicate()
    hosts = str(output.decode('ascii')).split('\n')
    hosts = [f'{host}:{port}' for host in hosts if host != '']
    if hosts == []:
        print('Hosts list is empty. Please check the inputs. Exiting...')
        exit(1)
    return hosts


if __name__ == '__main__':
    # Parse input arguments
    parser = arg_parser()
    args = parser.parse_args()
    num_nodes = args.n_nodes
    port = args.port
    assert num_nodes >= 1, "Must be more than 1"

    # Keep track of process ids
    pid_files = []

    # Fetch a list of available compute nodes
    hosts = generate_hosts(num_nodes, port)
    hosts.remove(f'{MASTER_IP}:{port}')  # Make sure the master IP isn't one of them

    # Launch the master node
    subprocess.Popen(shlex.split(
        f"ssh -f {MASTER_IP} ES_PATH_CONF={os.path.join(DB_SETUP_PATH, 'config_master1')} "
        f"{os.path.join(DB_SETUP_PATH, 'elasticsearch-8.1.0/bin/elasticsearch')} -Ehttp.port={port}-d -p pid"
        )
    )
    pid_files.append(os.path.join(os.path.abspath(os.path.curdir), 'pid'))
    print(f'[INFO] Launched the master node master-1 at {MASTER_IP}:{port}')

    # Launch the rest of the nodes (data nodes)
    for i in range(1, num_nodes):
        ip = hosts[i - 1].split(':')[0]  # Separate the hostname from port for the sake of the SSH connection

        # Launch the node
        subprocess.Popen(shlex.split(
            f"ssh -f {ip} ES_PATH_CONF={os.path.join(DB_SETUP_PATH, 'config_data1')} "
            f"{os.path.join(DB_SETUP_PATH, 'elasticsearch-8.1.0/bin/elasticsearch')} -Ehttp.port={port}-d -p pid{i} "
            f"-Enode.name=data-{i} -Epath.data='{os.path.join(DB_SETUP_PATH, 'elasticsearch-8.1.0/data_data' + str(i))}'"
            )
        )
        pid_files.append(os.path.join(os.path.abspath(os.path.curdir), f'pid{i}'))
        print(f'[INFO] Launched data node data-{i} at {ip}:{port}')
    
    # Parse and store all the pids
    pids = [int(pat.findall(f)[0]) for f in pid_files]

    # Keep this script running so that all the processes launched above can be stopped at once
    killer = GracefulKiller(pids)
    while not killer.exit_now:
        time.sleep(1)
    print("[INFO] Killed gracefully.")
    