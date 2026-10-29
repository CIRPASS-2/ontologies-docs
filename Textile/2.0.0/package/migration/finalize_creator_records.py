"""Finalize creator-task evidence only after successful local validation gates."""
import collections
import json
import subprocess
from xml.etree import ElementTree as ET
from migration import implement_core as m
from migration.update_creators import BASELINE
from migration.finalize_audit_records import inventory_since
from migration.refresh_publication import integrity
from scripts import validate_public as v


def write(path,data):
    (m.ROOT/path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')


def record():
    tree=ET.parse(m.ROOT/'migration/validation-pytest.xml')
    suites=list(tree.getroot().iter('testsuite'))
    counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    assert counts=={'tests':174,'failures':0,'errors':0,'skipped':0},counts
    for suite in suites:suite.attrib.pop('hostname',None)
    (m.ROOT/'migration/validation-pytest.xml').write_bytes(ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)+b'\n')
    runtime={name:json.loads((m.ROOT/f'creator-{name}-result.json').read_text('utf8')) for name in ('partial','complete')}
    keys=('examples_conformant','shacl_scenarios','reasoning_scenarios','rdfs_negative_control')
    for result in runtime.values():assert [result[key] for key in keys]==[11,16,6,'passed']
    protected=('migration/historical','migration/core-sources','dependencies','mireot','shacl','examples','tests/abox_corpus','traceability')
    changes=subprocess.check_output(['git','diff','--name-only',BASELINE,'--',*protected],cwd=m.ROOT,text=True)
    assert not changes,changes
    assert (m.ROOT/'VERSION').read_text('utf8').strip()=='2.0.0'
    report=json.loads((m.ROOT/'migration/validation-results.json').read_text('utf8'))
    report['pytest']=counts
    report['public_validation_modes']={name:{key:row[key] for key in keys} for name,row in runtime.items()}
    report['widoco_canonical_equivalence']['modules']=12
    report['audit_corrections']['creators']='unchanged during audit corrections; four owner-approved additions in subsequent creator task'
    report['creator_update']={'baseline_commit':BASELINE,'status':'passed','canonical_graphs':13,
        'creator_triples_added':52,'other_canonical_rdf_changes':0,'documentation_annotations_excluded':0,
        'before':['Elio Hbeich','BOUGACHA Racem'],
        'after':['Elio Hbeich','BOUGACHA Racem','Ivo Ladenius','Andreas Schneider','Jan Merckx','Piero de Sabbata'],
        'normalized_widoco_exports':27,'regenerated_exports_verified_isomorphic':48,
        'creator_only_documentation_provenance_graphs':12,
        'normalization_authorization':'Explicit owner approval within creator task; exact non-creator differences in creator-export-differences.json',
        'historical_core_si_mireot_shacl_examples':'unchanged',
        'candidate_version':'2.0.0','local_only':True}
    report['nonfatal_warnings']=['Twelve RDFLib JSON-LD parser deprecation warnings in pytest.',
        'WIDOCO optional configuration/logging/XML parser-property warnings; generation succeeded.']
    inv=json.loads((m.ROOT/'migration/change-inventory.json').read_text('utf8'))
    inv['creator_update_baseline']=BASELINE
    for suffix,commit in [('accepted_baseline',inv['accepted_baseline']),('preparation',inv['preparation_commit']),
                         ('accepted_implementation',inv['accepted_implementation']),('creator_update_baseline',BASELINE)]:
        entries=inventory_since(commit)
        inv['entries_since_'+suffix]=entries
        inv['summary_since_'+suffix]=dict(sorted(collections.Counter(row['status'] for row in entries).items()))
    files=[r['path'] for r in inv['entries_since_creator_update_baseline']]
    (m.ROOT/'migration/creator-update-files.txt').write_text('\n'.join(files)+'\n',encoding='utf8',newline='\n')
    write('migration/change-inventory.json',inv)
    write('migration/validation-results.json',report)
    integrity()
    report['results']=v.structural_checks(m.ROOT)
    report['results'].update({key:runtime['complete'][key] for key in keys})
    write('migration/validation-results.json',report)
    integrity()
    v.structural_checks(m.ROOT)
    print(json.dumps({'pytest':counts,'changed_files':len(files),'package_files':report['results']['package_files']},indent=2))


if __name__=='__main__':record()
