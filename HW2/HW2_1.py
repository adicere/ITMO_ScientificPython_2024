import request
import re
import json

#uni_ids=["P11473", "Q91XI3"]
#ens_ids=["ENSMUSG00000041147", "ENSG00000139618"]

def get_uniprot(ids: list):
    accessions = ','.join(ids)
    endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
    http_function = requests.get
    http_args = {'params': {'accessions': accessions}}
    return http_function(endpoint, **http_args)

def parse_response_uniprot(resp: dict):
    resp = resp.json()
    resp = resp["results"]
    output = {}
    for val in resp:
        acc = val['primaryAccession']
        species = val['organism']['scientificName']
        gene = val['genes']
        seq = val['sequence']
        output[acc] = {'organism':species, 'geneInfo':gene, 'sequenceInfo':seq, 'type':'protein'}

    return output

def get_ensembl(ids: list):
    endpoint = "https://rest.ensembl.org/lookup/id"
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}
    pre={"ids": ids}
    ready=json.dumps(pre)
    resp=requests.post(endpoint, headers=headers, data = ready)

    return resp

def parse_response_ensembl(resp: dict):
    resp = resp.json()
    output = {}
    for val in resp.values():
        id = val['id']
        species = val['species']
        gene = {
            'assembly_name':val['assembly_name'],
            'name':val['display_name'],
            'description':val['description']
        }
        seq = {
            'start':val['start'],
            'end':val['end']
        }
        object_type = val['object_type']
        output[id] = {'organism': species, 'geneInfo': gene, 'sequenceInfo': seq, 'type': object_type}

    return output

def regulars(ids: list):
    dbRegEx = {"uniprot":"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}",
               "ensembl":"ENS[A-Z]{,6}[0-9]{11}|MGP\w+[0-9]{11}"}
    if re.fullmatch(dbRegEx["uniprot"], ids[0])!=None:
        return parse_response_uniprot(get_uniprot(ids))
    else:
        if re.fullmatch(dbRegEx["ensembl"], ids[0])!=None:
            return parse_response_ensembl(get_ensembl(ids))
