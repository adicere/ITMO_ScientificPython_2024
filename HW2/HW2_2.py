from Bio import SeqIO
import subprocess
import requests
import re
import json
import os

def fasta_info(fasta_file):
  path=os.path.basename(fasta_file)
  seqkit = subprocess.run(("seqkit", "stats", path, "-a"), capture_output=True, text=True)
  if seqkit.stderr!='':
    error=seqkit.stderr
    pattern = r': (.+)$'
    match = re.search(pattern, error)
    if match:
      error_message = match.group(1)
      print(f'Sorry! Cannot find any information due to this error: {error_message}')
  else:
    seqkit_out = seqkit.stdout.strip().split('\n')
    prop_names = seqkit_out[0].split()[1:]
    prop_vals = seqkit_out[1].split()[1:]
    seq_result= dict(zip(prop_names, prop_vals))

    print(f'Info for {path}') 
    print()
    print('Statistics:')
    for key, value in seq_result.items():
      print(f'{key}: {value}')


    get_ids(fasta_file, seq_result)

def get_ids(fasta_file, seq_stats):
  file_name = os.path.basename(fasta_file)
  ext = 'fasta'
  sequences = SeqIO.parse(file_name, ext) 
  IDS=[]
  if seq_stats['type']=='Protein':
    print()
    print('Uniprot DB info:')
    pattern=r'[A-Z0-9]{6}'
    for seq in sequences:
      seq_id=seq.id
      match = re.search(pattern, seq_id)
      if match:
        matched = match.group(0)
        IDS.append(matched)
    get_uniprot(IDS)
    return IDS
  if seq_stats['type']=='DNA':
    print()
    print('ENSEMBL info:')
    for seq in sequences:
      seq_id=seq.id
      IDS.append(seq_id)
    IDS = [re.sub(r'\.\d+', '', id) for id in IDS]
    get_ensembl(IDS)
    return IDS

def get_uniprot(ids: list):
  accessions = ','.join(ids)
  endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
  http_function = requests.get
  http_args = {'params': {'accessions': accessions}}
  resp=http_function(endpoint, **http_args)
  parse_response_uniprot(resp)
  return http_function(endpoint, **http_args)

def parse_response_uniprot(resp: dict):
  resp = resp.json()
  resp = resp["results"]
  output = {}
  for val in resp:
      acc = val['primaryAccession']
      gene = val['genes']
      seq = val['sequence']
      output[acc] = {'geneInfo':gene, 'sequenceInfo':seq, 'type':'protein'}

  for key, value in output.items():
    print(f'{key}: {value}')
    print()
  return output
 
def get_ensembl(ids: list):
  endpoint = "https://rest.ensembl.org/lookup/id"
  headers={ "Content-Type" : "application/json", "Accept" : "application/json"}
  pre={"ids": ids}
  ready=json.dumps(pre)
  resp=requests.post(endpoint, headers=headers, data = ready)
  parse_response_ensembl(resp)
  return resp

def parse_response_ensembl(resp: dict):
  resp = resp.json()
  output = {}
  for val in resp.values():
      id = val['id']
      species = val['species']
      gene = {
          'assembly_name':val['assembly_name'],
          'name':val['display_name']}
      object_type = val['object_type']
      output[id] = {'organism': species, 'geneInfo': gene,  'type': object_type}

  for key, value in output.items():
    print(f'{key}: {value}')
    print()
  return output


fasta_info('./hw_file2.fasta')