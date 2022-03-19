# db-setup

## Elasticsearch

1. Download ElasticSearch:

   ```bash
   > wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.1.0-linux-x86_64.tar.gz
   > tar -xzf elasticsearch-8.1.0-linux-x86_64.tar.gz
   > cd elasticsearch-8.1.0/ 
   > 
   ```

2. Launch master:

   ```bash
   > ES_PATH_CONF=/home/sja082/db-assignment/elasticsearch-8.1.0/config_master1 bin/elasticsearch -d -p pid
   ```

3. Launch data nodes:

   Use the following command, substituting {num} with different integers for different data nodes.

   ```bash
   > ES_PATH_CONF=/home/sja082/db-assignment/elasticsearch-8.1.0/config_data1/ bin/elasticsearch -d -p pid{num} -Enode.name=data-{num} -Epath.data="/home/sja082/db-assignment/elasticsearch-8.1.0/data_data{num}"
   ```
