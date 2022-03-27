import argparse
import subprocess
import shlex
import os
import signal
from sys import exit, stdout
import re
import time

# Some parameters
PORT_DEFAULT = 8529
NODES_DEFAULT = 3
MASTER_IP = 'compute-3-12'
DB_SETUP_PATH = '/home/sja082/db-assignment/db-setup/'
# DIE_AFTER_SECONDS_DEFAULT = 20 * 60

pat = re.compile('(\d+)')

def arg_parser():
    parser = argparse.ArgumentParser(prog="Main script", description="main script responsible for launching the elasticsearch database cluster")

    parser.add_argument("-n", "--n-nodes", type=int, default=NODES_DEFAULT,
        help="total number of nodes, default %d" % NODES_DEFAULT
    )

    parser.add_argument("--hosts-list", type=str, default=None,
        help="A file containing a list of hosts to choose from, one per line. If not provided, a random list of hosts will be used."
    )


    # parser.add_argument("-p", "--port", type=int, default=PORT_DEFAULT,
    #         help="port number to use, default %d" % PORT_DEFAULT
    # )

    # parser.add_argument("-d", "--die-after-seconds", type=float,
    #         default=DIE_AFTER_SECONDS_DEFAULT,
    #         help="kill server after so many seconds have elapsed, " +
    #             "in case we forget or fail to kill it, " +
    #             "default %d (%d minutes)" % (DIE_AFTER_SECONDS_DEFAULT, DIE_AFTER_SECONDS_DEFAULT/60)
    # )

    return parser


class GracefulKiller():
    def __init__(self, kill_cmds):
        self.kill_cmds = kill_cmds
        self.exit_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        for cmd in self.kill_cmds:
            subprocess.Popen(shlex.split(cmd))

        # Clear the data directories and configs
        try:
            subprocess.Popen(shlex.split(f"rm  -r $HOME/arangodb3-linux-3.9.0/data*"))
        except Exception as e:
            print(f'{e} occured while deleting ~/arangodb3-linux-3.9.0/data*. Ignoring...')
        
        try:
            subprocess.Popen(shlex.split(f"rm  -r {os.path.join(DB_SETUP_PATH, 'arangodb3-linux-3.9.0/data*')}"))
        except Exception as e:
            print(f'{e} occured while deleting ./arangodb3-linux-3.9.0/data*. Ignoring...')
        
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


def read_hosts(hosts_list, port):
    with open(hosts_list) as f:
        hosts = f.read().strip(' ').split('\n')
        hosts = [f"{h.strip(' ')}:{port}" for h in hosts if h != '']
        return hosts



if __name__ == '__main__':
    # Parse input arguments
    parser = arg_parser()
    args = parser.parse_args()
    num_nodes = args.n_nodes
    port = PORT_DEFAULT  # Currently, cannot change the port as the ArangDB starter script doesn't allow that
    assert num_nodes >= 1, "Must be more than 1"

    # Clear the data directories and configs
    try:
        subprocess.Popen(shlex.split(f"rm  -r $HOME/arangodb3-linux-3.9.0/data*"))
    except Exception as e:
        pass
    
    try:
        subprocess.Popen(shlex.split(f"rm  -r {os.path.join(DB_SETUP_PATH, 'arangodb3-linux-3.9.0/data*')}"))
    except Exception as e:
        pass

    # Keep track of processes launched
    kill_cmds = []

    # Fetch a list of available compute nodes
    if args.hosts_list is not None:
        hosts = read_hosts(args.hosts_list, port)
    else:
        hosts = generate_hosts(num_nodes, port)
    
    if f'{MASTER_IP}:{port}' in hosts:  # Make sure the master IP isn't one of them
        hosts.remove(f'{MASTER_IP}:{port}')

    # Launch the master node
    subprocess.Popen(shlex.split(
        f"ssh -f {MASTER_IP} {os.path.join(DB_SETUP_PATH, 'arangodb3-linux-3.9.0/bin/arangodb')} "
        f"--server.storage-engine=rocksdb --starter.data-dir={os.path.join(DB_SETUP_PATH, 'arangodb3-linux-3.9.0/data')}"
        )
    )
    kill_cmds.append(f"ssh -f {MASTER_IP} pkill arangodb")
    print(f'[INFO] Launched the master node at {MASTER_IP}:{port}')

    # Launch the rest of the nodes (data nodes)
    for i in range(1, num_nodes):
        ip = hosts[i - 1].split(':')[0]  # Separate the hostname from port for the sake of the SSH connection

        # Launch the node
        subprocess.Popen(shlex.split(
            f"ssh -f {ip} {os.path.join(DB_SETUP_PATH, 'arangodb3-linux-3.9.0/bin/arangodb')} "
            f"--server.storage-engine=rocksdb --starter.data-dir={os.path.join(DB_SETUP_PATH, 'arangodb3-linux-3.9.0/data')}{i} "
            f"--starter.join {MASTER_IP}"
            )
        )
        kill_cmds.append(f"ssh -f {ip} pkill arangodb")
        print(f'[INFO] Launched data node {i} at {ip}:{port}')

    # Keep this script running so that all the processes launched above can be stopped at once
    killer = GracefulKiller(kill_cmds)
    while not killer.exit_now:
        time.sleep(1)
    print("[INFO] Killed gracefully.")
    