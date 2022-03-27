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
PORT_DEFAULT = 55781
NODES_DEFAULT = 3
MASTER_IP = 'compute-3-12'
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


# Manual

Not recommended. Scripts mentioned above work just fine.

## 1. ElasticSearch

1. Download ElasticSearch:

   ```bash
   > wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.1.0-linux-x86_64.tar.gz
   > tar -xzf elasticsearch-8.1.0-linux-x86_64.tar.gz
   > cd elasticsearch-8.1.0/
   ```

2. Update the `path.data` argument inside `config_master1/elasticsearch.yml` appropriately (for e.g., change sja082 with your username and update the path to correctly point to the `elasticsearch-8.1.0` folder etc.)

3. Launch master:

   May need to change `ES_PATH_CONF` depending on your directory structure.

   ```bash
   > ssh -f compute-3-12 ES_PATH_CONF=/home/sja082/db-assignment/db-setup/elastic_config_master1 $(pwd)/bin/elasticsearch -d -p pid
   ```

4. Launch data nodes:

   > **Note**: Currently hardcoded to assume the master to be running on compute-3-12

   Use the following command, substituting {num} with different integers for different data \<node>s.

   May need to change `ES_PATH_CONF` and path.data depending on your directory structure.

   ```bash
   > ssh -f compute-<node> ES_PATH_CONF=/home/sja082/db-assignment/db-setup/elastic_config_data1 $(pwd)/bin/elasticsearch -d -p pid{num} -Enode.name=data-{num} -Epath.data="/home/sja082/db-assignment/db-setup/elasticsearch-8.1.0/data_data{num}"
   ```

5. Kill nodes once done:

   master:

   ```bash
   > ssh -f compute-3-12 kill $(cat pid)
   ```

   data nodes: 

   Substitute {num} with different integers for different data \<node>s (same as used earlier). 

   ```bash
   > ssh -f compute-<node> kill $(cat pid{num})
   ```

## 2. ArangoDB

1. Download ArangoDB

   ```bash
   > wget https://download.arangodb.com/arangodb39/Community/Linux/arangodb3-linux-3.9.0.tar.gz
   > cd arangodb3-linux-3.9.0
   ```

2. Create ArangoDB secret

   ```bash
   > bin/arangodb create jwt-secret --secret=arangodb.secret
   > chmod 400 arangodb.secret
   ```

3. s