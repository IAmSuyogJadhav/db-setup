# db-setup

# Scripts
Use these scripts to quickly launch databases.

## ElasticSearch

```bash
   usage: python scripts/start_elasticsearch.py [-h] [-n N_NODES] [-p PORT]

   options:
   -h, --help            show this help message and exit
   -n N_NODES, --n-nodes N_NODES
               total number of nodes, default 3
   -p PORT, --port PORT  
               port number to use, default 55781
```
There are some parameters set inside the `scripts/start_elasticsearch.py` that may be modified as wished.
PORT_DEFAULT = 55781
NODES_DEFAULT = 3
MASTER_IP = 'compute-3-12'
DB_SETUP_PATH = '/home/sja082/db-assignment/db-setup/'


# Manual
Not recommended. Scripts mentioned above work just fine.

## ElasticSearch

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


4. Kill nodes once done:

   master:

   ```bash
   > ssh -f compute-3-12 kill $(cat pid)
   ```

   data nodes: 

   Substitute {num} with different integers for different data \<node>s (same as used earlier). 

   ```bash
   > ssh -f compute-<node> kill $(cat pid{num})
   ```

   