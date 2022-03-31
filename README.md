# db-setup

# Scripts

Use these scripts to quickly launch databases.

## 1. ElasticSearch

Download ElasticSearch

```bash
> wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.1.0-linux-x86_64.tar.gz
> tar -xzf elasticsearch-8.1.0-linux-x86_64.tar.gz
```

Run the script:

```bash
   usage: python scripts/start_elasticsearch.py [-h] [-n N_NODES] [-p PORT]

   options:
   -h, --help            show this help message and exit
   -n N_NODES, --n-nodes N_NODES
               total number of nodes, default 3
   -p PORT, --port PORT  
               port number to use, default 55781
  --hosts-list HOSTS_LIST
  				A file containing a list of hosts to choose from, one per line. If not provided, a random list of hosts will be used.

```
These are some parameters set inside the `scripts/start_elasticsearch.py` that may be modified as wished:

```python
PORT_DEFAULT = 8529
NODES_DEFAULT = 3
MASTER_IP = 'compute-10-16'
DB_SETUP_PATH = '/home/sja082/db-assignment/db-setup/'
```

To kill, simply press `Ctrl + C`. The script will kill all the nodes launched and exit.

## 2. ArangoDB

Download ArangoDB

```bash
> wget https://download.arangodb.com/arangodb39/Community/Linux/arangodb3-linux-3.9.0.tar.gz
> tar -xzf arangodb3-linux-3.9.0.tar.gz
```

Run the script (the port can't be changed currently since the started arangodb binary does not allow it. The default port is 8529):

```bash
   usage: python scripts/start_arangodb.py [-h] [-n N_NODES]

   options:
   -h, --help            show this help message and exit
   -n N_NODES, --n-nodes N_NODES
               total number of nodes, default 3
  --hosts-list HOSTS_LIST
  				A file containing a list of hosts to choose from, one per line. If not provided, a random list of hosts will be used.

```

## 3. Redis

The variables can be set inside the script `scripts/redis-deploy.sh`. Install Redis and run the script to launch the cluster.

```bash
> bash scripts/redis-deploy.sh 
```