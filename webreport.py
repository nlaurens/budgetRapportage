import web
from config import config

def groep_report(render):
    report = {}
    report['settings'] = 'settings!!'
    report['summary'] = 'summary!!'
    report['body'] = render.report_table()
    return report
