import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import update_jobs as j

TEXT=('We require fluent English communication skills. You will coordinate project stakeholders, '
      'deliver project milestones, track KPI reports, improve workflow processes and automate Excel reports. '
      'We offer strong career growth and flexible hours. ')*3

class FilterTests(unittest.TestCase):
 def test_language_english_only(self):
  self.assertTrue(j.language_ok(TEXT))
  self.assertFalse(j.language_ok(TEXT+' Fluent German required for all applicants.'))
  self.assertFalse(j.language_ok(TEXT+' Fluent French required for all applicants.'))
 def test_location(self):
  self.assertTrue(j.in_germany('Berlin'))
  self.assertTrue(j.in_germany('Remote Germany'))
  self.assertFalse(j.in_germany('London, UK'))
  self.assertFalse(j.in_germany('Remote anywhere in Europe'))
 def test_recent_date(self):
  self.assertTrue(j.recent(j.TODAY.isoformat()))
  self.assertTrue(j.recent(j.MIN_DATE.isoformat()))
  self.assertFalse(j.recent((j.MIN_DATE-dt.timedelta(days=1)).isoformat()))
 def test_good_role_and_bad_role(self):
  self.assertIsNotNone(j.score_role('Junior Project Manager', TEXT))
  self.assertIsNone(j.score_role('Senior Project Manager', TEXT))
  self.assertIsNone(j.score_role('Project Coordinator', TEXT+' At least 5 years experience required.'))
 def test_arbeitnow_record(self):
  record={'slug':'acme-berlin','title':'Project Coordinator','company_name':'Acme',
  'created_at':int(j.NOW.timestamp()),'url':'https://example.org/position','location':'Berlin',
  'job_types':['Full-time'],'description':'<p>'+TEXT+'</p>', 'tags':[]}
  found=j.from_arbeitnow(record)
  self.assertIsNotNone(found)
  self.assertGreaterEqual(found['score'],85)
  record['description']+='<p>Fluent German required.</p>'
  self.assertIsNone(j.from_arbeitnow(record))

if __name__=='__main__': unittest.main()
