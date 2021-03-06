# -*- coding: utf-8 -*-

"""
1. Find the name of a file to test with.
2. Get that file
3. Update the config.yml to say task types are 'scrape' and 'modify'
4. Run
5. Delete record from sc2
6. Insert on sc2
7. Update on sc2
"""
import io
import logging
import sys
from astropy.table import Table
from cadcutils import net
from cadcdata import CadcDataClient
from cadctap import CadcTapClient
from caom2repo import CAOM2RepoClient
from caom2pipe import manage_composable as mc

collection = sys.argv[1].upper()
if collection == 'NEOSSAT':
    service = 'shared'
    archive = 'NEOSSAT'
    collection = 'NEOSS'
elif collection == 'GEM':
    service = 'gemini'
    archive = 'GEMINI'
elif collection == 'VLASS':
    service = 'cirada'
    archive = 'VLASS'
else:
    service = collection.lower()
    archive = collection
proxy_fqn = '/usr/src/app/cadcproxy.pem'
subject = net.Subject(certificate=proxy_fqn)
ad_client = CadcTapClient(subject, resource_id='ivo://cadc.nrc.ca/ad')
ops_client = CadcTapClient(subject, resource_id=f'ivo://cadc.nrc.ca/ams/{service}')
caom_client = CAOM2RepoClient(subject, resource_id='ivo://cadc.nrc.ca/ams')

print(':::1 - Find the name of a file to test with.')
ops_query = f"SELECT O.observationID, A.uri " \
f"FROM caom2.Observation as O " \
f"JOIN caom2.Plane as P on O.obsID = P.obsID " \
f"JOIN caom2.Artifact as A on P.planeID = A.planeID " \
f"WHERE O.collection = '{archive}' " \
f"AND A.uri like '%.fits%' " \
f"LIMIT 1"

ops_buffer = io.StringIO()
ops_client.query(ops_query, output_file=ops_buffer, data_only=True, response_format='csv')
ops_table = Table.read(ops_buffer.getvalue().split('\n'), format='csv')
if len(ops_table) == 1:
    obs_id = ops_table[0]['observationID']
    uri = ops_table[0]['uri']
    ignore_scheme, ignore_path, f_name = mc.decompose_uri(uri)
    print(f':::Looking for {obs_id} and {f_name}')
else:
    print(f':::No observation records found for collection {archive}')
    sys.exit(-1)

obs = caom_client.read(archive, obs_id)
obs_fqn = f'/usr/src/app/expected.{obs_id}.xml'
mc.write_obs_to_file(obs, obs_fqn)

print(f':::2 - Get {f_name}')
config = mc.Config()
config.get_executors()
data_client = CadcDataClient(subject)
metrics = mc.Metrics(config)
mc.data_get(data_client, '/usr/src/app', f_name, collection, metrics)

print(':::3 - Update config.yml to say task types are scrape and modify, and use local files.')
config.task_types = [mc.TaskType.SCRAPE, mc.TaskType.MODIFY]
config.use_local_files = True
config.logging_level = logging.INFO
mc.Config.write_to_file(config)

print(':::4 - Run the application.')
sys.exit(0)
