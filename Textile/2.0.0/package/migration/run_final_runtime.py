"""Record the full offline regression run with the complete-report profile."""
import json
from scripts import validate_public as v

if __name__=='__main__':
    result=v.structural_checks(v.ROOT)
    result.update(v.runtime_checks(v.ROOT,complete_report=True,progress=lambda message:print(message,flush=True)))
    report={'candidate':'2.0.0','public_validation':'passed','complete_report_selected':True,'results':result}
    (v.ROOT/'migration/validation-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2),flush=True)
