"""Record successful audit gates and the complete local change inventory."""
import collections
import json
import subprocess
from xml.etree import ElementTree as ET
from migration import implement_core as m
from migration.refresh_publication import integrity
from scripts import validate_public as v


def write(path,value):
    (m.ROOT/path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def inventory_since(commit):
    result=subprocess.run(['git','diff','--name-status','--no-renames',commit],cwd=m.ROOT,capture_output=True,text=True,check=True)
    rows={line.split('\t',1)[1]:line.split('\t',1)[0] for line in result.stdout.splitlines()}
    new=subprocess.run(['git','ls-files','--others','--exclude-standard'],cwd=m.ROOT,capture_output=True,text=True,check=True)
    package=set(v.package_files(m.ROOT))
    # These records are written after inventory calculation on the first run.
    for path in ('migration/change-inventory.json','migration/validation-results.json'):
        exists=subprocess.run(['git','cat-file','-e',commit+':'+path],cwd=m.ROOT,capture_output=True).returncode==0
        rows.setdefault(path,'M' if exists else 'A')
    for path in new.stdout.splitlines():
        if path in package:rows[path]='A'
    return [{'path':p,'status':s} for p,s in sorted(rows.items()) if p in package or s=='D' or p=='.gitattributes']


def record():
    pytest_path=m.ROOT/'migration/validation-pytest.xml'
    tree=ET.parse(pytest_path);suites=list(tree.getroot().iter('testsuite'))
    counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    assert counts=={'tests':164,'failures':0,'errors':0,'skipped':0},counts
    for suite in suites:suite.attrib.pop('hostname',None)
    pytest_path.write_bytes(ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)+b'\n')
    runtime={name:json.loads((m.ROOT/f'audit-{name}-result.json').read_text('utf8')) for name in ('partial','complete')}
    keys=('examples_conformant','shacl_scenarios','reasoning_scenarios','rdfs_negative_control')
    for result in runtime.values():assert [result[k] for k in keys]==[11,16,6,'passed']
    report=json.loads((m.ROOT/'migration/validation-results.json').read_text('utf8'))
    report['pytest']=counts
    report['accepted_implementation']='5bac1a2cba2332b3e5ad7d45d305fbb786ee59f2'
    report['public_validation_modes']={name:{key:result[key] for key in keys} for name,result in runtime.items()}
    report['audit_corrections']={'major_findings':3,'targeted_minor_findings':8,'status':'corrected',
       'copied_external_definitions_attributed':42,'historical_mapping_inventory_resources':96,
       'historical_root_closure_graphs':19,'historical_soc_closure_graphs':12,
       'CE6':{'accepted_conforms':True,'corrected_conforms':False},
       'CE7':{'accepted_conforms':False,'corrected_conforms':True},
       'CE8':{'accepted_conforms':False,'corrected_conforms':True},
       'historical_and_core_bytes':'unchanged','creators':'unchanged',
       'constraint_coverage':'targeted; not claimed to be complete',
       'temporary_directory_note':'Sandbox runs encountered four temporary-directory setup errors, including with a fresh workspace directory; the successful full run used approved normal Windows access.'}
    inv=json.loads((m.ROOT/'migration/change-inventory.json').read_text('utf8'))
    inv['accepted_implementation']=report['accepted_implementation']
    for suffix,commit in [('accepted_baseline',inv['accepted_baseline']),('preparation',inv['preparation_commit']),('accepted_implementation',inv['accepted_implementation'])]:
        entries=inventory_since(commit)
        inv['entries_since_'+suffix]=entries
        inv['summary_since_'+suffix]=dict(sorted(collections.Counter(row['status'] for row in entries).items()))
    write('migration/change-inventory.json',inv)
    path=m.ROOT/'migration/AUDIT_CORRECTIONS.md'
    text=path.read_text('utf8')
    marker='Machine-readable results are in [validation results](validation-results.json)'
    if 'The full suite passes **164 tests**' not in text:
        text=text.replace(marker,'The full suite passes **164 tests**, including the original 111 regressions.\nBoth partial and complete-report public modes pass.\n\n'+marker)
    path.write_text(text,encoding='utf8',newline='\n')
    integrity()
    report['results']=v.structural_checks(m.ROOT)
    report['results'].update({key:runtime['complete'][key] for key in keys})
    write('migration/validation-results.json',report)
    integrity()
    v.structural_checks(m.ROOT)
    print(json.dumps({'pytest':counts,'correction_files':len(inv['entries_since_accepted_implementation']),'package_files':report['results']['package_files']},indent=2))


if __name__=='__main__':record()
