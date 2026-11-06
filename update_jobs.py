#!/usr/bin/env python3
"""JobPilot: screen public Germany job feeds and produce jobs.json for GitHub Pages.

No API keys. Conservative rules: no German requirement, dated within 14 calendar
days, graduate / entry-level / junior / associate roles, estimated CV fit >=70. Feed posting dates are NOT verified
employer-original posting dates. Source outages are disclosed in metadata.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo('Europe/Berlin')
NOW = dt.datetime.now(BERLIN)
TODAY = NOW.date()
MIN_DATE = TODAY - dt.timedelta(days=13)
OUT = Path(__file__).with_name('jobs.json')

class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_data(self, data):
        self.parts.append(data)

def clean(s):
    p=TextHTML(); p.feed(str(s or ''))
    return re.sub(r'\s+',' ',html.unescape(' '.join(p.parts))).strip()

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'JobPilot/1.0 (+GitHub Actions; personal job search)', 'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=22) as r:
        if r.status!=200: raise RuntimeError(f'HTTP {r.status}')
        return json.load(r)

def date_of(value):
    try:
        if isinstance(value,(int,float)): return dt.datetime.fromtimestamp(value,dt.timezone.utc).astimezone(BERLIN).date()
        if isinstance(value,str) and value[:10]: return dt.date.fromisoformat(value[:10])
    except (ValueError,TypeError,OverflowError): pass
    return None

def recent(value):
    d=date_of(value)
    return bool(d and MIN_DATE<=d<=TODAY)

GERMAN_LOCATIONS=('berlin','germany','deutschland','munich','münchen','hamburg','frankfurt',
 'stuttgart','cologne','köln','bonn','düsseldorf','duesseldorf','dresden','leipzig','dortmund','bremen',
 'potsdam','darmstadt','aachen','karlsruhe','nuremberg','nürnberg','freiburg','heidelberg','mainz',
 'mannheim','hanover','hannover','wiesbaden','essen','ulm','regensburg','braunschweig','ingolstadt',
 'rostock','kiel','wuppertal','münster','muenster','bielefeld','göttingen','goettingen','bochum','augsburg')
CITIES=('Berlin','Munich','Hamburg','Frankfurt','Stuttgart','Cologne','Köln','Bonn','Düsseldorf','Dresden',
 'Leipzig','Dortmund','Bremen','Potsdam','Darmstadt','Aachen','Karlsruhe','Nuremberg','Nürnberg',
 'Freiburg','Heidelberg','Mainz','Mannheim','Hanover','Hannover','Wiesbaden','Essen','Ulm',
 'Regensburg','Kiel','Rostock','Bochum','Augsburg','Münster')
UNSUITABLE_LOC=re.compile(r'\b(?:london|manchester|amsterdam|vienna|paris|madrid|barcelona|lisbon|warsaw|zurich|zürich|uk|united kingdom|usa|new york|poland|netherlands|austria|france|switzerland)\b',re.I)

def in_germany(location):
    s=str(location or '').strip().lower()
    if not s: return False
    return (not UNSUITABLE_LOC.search(s) and any(x in s for x in GERMAN_LOCATIONS))

def city_of(location):
    s=str(location or '').lower()
    return next((c for c in CITIES if c.lower() in s),'Germany')

TITLE_GOOD=re.compile(r'\b(?:project\s+(?:coordinator|officer|assistant|associate|analyst)|(?:junior|graduate|associate)\s+project\s+manager|project\s+management\s+(?:associate|intern|coordinator)|pmo\b|program(?:me)?\s+(?:associate|assistant|coordinator|officer|analyst|intern)|(?:junior|graduate)\s+program(?:me)?\s+manager|business\s+operations|operations\s+(?:associate|analyst|coordinator|specialist|intern)|(?:graduate|junior|entry[- ]level|associate)\s+(?:business|operations|project|product|process|trading|strategy|marketing|growth)\s+(?:analyst|associate|coordinator|manager|specialist|intern|consultant)|(?:junior|associate|graduate)\s+product\s+(?:manager|analyst)|product\s+management\s+intern|product\s+operations\s+(?:associate|analyst|coordinator|intern)|(?:junior|business|strategy|consulting|product|marketing|growth)\s+analyst|strategy\s+and\s+operations\s+(?:associate|analyst|intern)|founder\'?s?\s+(?:associate|intern)|(?:junior|graduate|associate)\s+(?:strategy|management|business)\s+consultant|(?:junior|graduate|associate)\s+consultant|consulting\s+(?:analyst|associate|intern)|marketing\s+(?:coordinator|associate|analyst|intern)|growth\s+(?:associate|analyst|intern|coordinator)|(?:digital|product|performance|growth)\s+marketing\s+(?:coordinator|associate|analyst|intern|specialist)|operations\s+and\s+events\s+associate)\b',re.I)
TITLE_BAD=re.compile(r'\b(?:senior|sr\.|principal|staff|head of|director|vp|vice president|expert|architect|technical lead|manager of|engineer|scientist|accountant|bookkeeper|tax|legal|doctor|technician|developer|sales development|account executive|customer service representative|purchasing manager)\b',re.I)
YEARS_HIGH=re.compile(r'\b(?:[4-9]|1\d)\s*\+?\s*(?:years|yrs)\s+(?:of\s+)?(?:relevant\s+)?experience\b|\b(?:minimum|at least)\s+(?:[4-9]|1\d)\s+years\b',re.I)
GERMAN_AD=re.compile(r'\b(?:du bringst mit|deine aufgaben|wir suchen dich|sehr gute deutschkenntnisse|sie verfügen über|verhandlungssicheres deutsch|bitte bewerben sie|wir bieten dir)\b',re.I)
ENGLISH_REQUIRED=re.compile(r'\b(?:english\s+(?:is\s+)?(?:required|essential|mandatory|fluency|proficiency)|fluent\s+(?:in\s+)?english|professional\s+(?:working\s+)?(?:fluency|proficiency)\s+in\s+english|excellent\s+(?:written\s+and\s+spoken\s+)?english|strong\s+(?:written\s+and\s+verbal\s+)?communication\s+(?:skills\s+)?in\s+english|good\s+(?:communication\s+)?(?:skills\s+)?in\s+english|excellent\s+english\s+skills|fluency\s+in\s+english)\b',re.I)
GERMAN_REQUIRED=re.compile(r'\b(?:fluent|fluency|proficien(?:t|cy)|native|excellent|business[- ]fluent|professional|mandatory|required|c1|c2)\b.{0,26}\b(?:german|deutsch)\b|\b(?:german|deutsch)\b.{0,25}\b(?:fluent|fluency|proficien(?:t|cy)|mandatory|required|essential|c1|c2)\b|(?:speak|write|communicat\w*)\s+(?:both\s+)?(?:german\s+and\s+english|english\s+and\s+german)',re.I)
OTHER_REQUIRED=re.compile(r'\b(?:french|mandarin|spanish|italian|dutch|portuguese|polish|arabic|turkish)\b.{0,18}\b(?:required|mandatory|fluency|fluent|native|c1|c2)\b|\b(?:fluent|native|proficiency)\b.{0,18}\b(?:french|mandarin|spanish|italian|dutch|portuguese|polish|arabic|turkish)\b',re.I)


def language_ok(txt,tags=()):
    if len(txt)<120 or GERMAN_AD.search(txt): return False
    english=bool(ENGLISH_REQUIRED.search(txt) or any('english speaking' in str(t).lower() for t in tags))
    if not english: return False
    # Avoid treating a "nice to have" language as mandatory. Conservative: reject borderline ads.
    required_section=re.split(r'\b(?:nice to have|beneficial skills|desirable|what we offer|benefits|nice-to-have)\b',txt,maxsplit=1,flags=re.I)[0]
    if GERMAN_REQUIRED.search(required_section) or OTHER_REQUIRED.search(required_section): return False
    return True


def score_role(title,text):
    """Heuristic CV relevance estimate; never a hiring probability."""
    if not TITLE_GOOD.search(title) or TITLE_BAD.search(title) or YEARS_HIGH.search(text): return None
    if re.search(r'\b(?:currently enrolled|must be enrolled|be a registered student|student enrollment required|enrolled in a university)\b',text,re.I): return None
    if re.search(r'\bprogram(?:me)?\b',title,re.I): cat='Programme Coordination'
    elif re.search(r'pmo|project',title,re.I): cat='Project Management'
    elif re.search(r'product',title,re.I): cat='Product Management'
    elif re.search(r'strategy|consult|founder',title,re.I): cat='Strategy & Consulting'
    elif re.search(r'marketing|growth',title,re.I): cat='Marketing & Growth'
    elif re.search(r'business analyst|business intelligence|consulting analyst',title,re.I): cat='Business Analysis'
    else: cat='Operations'
    score=65;why=[]
    if cat in ('Project Management','Programme Coordination'):
        score+=10;why.append('project and programme coordination')
    elif cat=='Operations':
        score+=9;why.append('operational improvements and cross-team delivery')
    elif cat=='Business Analysis':
        score+=8;why.append('Excel reporting and structured analysis')
    elif cat=='Product Management':
        score+=8;why.append('cross-functional MVP/product delivery')
    elif cat=='Marketing & Growth':
        score+=7;why.append('go-to-market, marketing and growth campaigns')
    elif cat=='Strategy & Consulting':
        score+=6;why.append('business model assessment and management studies')
    if re.search(r'stakeholder|cross-functional|project management|project planning|milestone|programme management',text,re.I):
        score+=4;why.append('stakeholders and project tracking')
    if re.search(r'kpi|reporting|excel|spreadsheet|dashboard|analyt',text,re.I):
        score+=4;why.append('reporting and analytics')
    if re.search(r'process improvement|workflow|automation|jira|operations',text,re.I):
        score+=3;why.append('workflow and process improvement')
    if re.search(r'go.to.market|marketing|growth|campaign|seo|market research',text,re.I):
        score+=3;why.append('marketing and growth execution')
    if re.search(r'startup|business model|research project|sustainab|strategy',text,re.I): score+=2
    if score<70:return None
    return min(score,96),cat,why


def from_arbeitnow(j):
    if not all((j.get('title'),j.get('created_at'),j.get('url'))):return None
    date=date_of(j['created_at'])
    if not recent(date.isoformat()) or not in_germany(j.get('location')):return None
    title=str(j['title']); desc=clean(j.get('description'))
    if not language_ok(desc,j.get('tags') or ()):return None
    role=score_role(title,desc)
    if not role:return None
    types=' '.join(j.get('job_types') or ())
    internship=bool(re.search(r'\b(?:intern|internship|trainee|praktik)\b',title+' '+types,re.I))
    if re.search(r'working student|werkstudent|part[- ]time|teilzeit|minijob',title+' '+types,re.I) and not internship:return None
    score,cat,why=role
    return dict(id='arbeitnow-'+str(j.get('slug') or j['url']),title=title,company=j.get('company_name') or 'Company not stated',
      city=city_of(j.get('location')),location=str(j.get('location') or 'Germany'),category=cat,
      employment='Internship' if internship else 'Full-time / verify',
      workplace='Remote / verify Germany eligibility' if j.get('remote') else 'On-site / hybrid not specified',
      posted=date.isoformat(),url=str(j['url']),detailsUrl=str(j['url']),score=score,
      reason='Estimated CV fit based on '+', '.join(why[:3])+'. Experience includes UNU research coordination, cross-functional delivery, Jira and Excel reporting.',
      watchout='Automatically screened; listing date is the job-board publication date, not confirmed employer-original posting date. Verify qualifications and job status.',
      skills=[],source='Arbeitnow (board publication)',reviewed=False,deadline='',language='English explicitly requested; no mandatory German detected',
      dateEvidence='Arbeitnow created_at; employer-original posting date unverified')


def from_intern(j):
    posted=j.get('posted_at') or j.get('first_seen_at')
    if not recent(posted) or (j.get('location') or {}).get('country_code')!='DE': return None
    langs=j.get('languages') or {}
    if langs.get('german')=='required' or langs.get('english')!='required':return None
    if (j.get('details') or {}).get('enrolment')=='required': return None
    title=j.get('title') or ''
    text=' '.join(j.get('skills') or ())+' '+str(j.get('field') or '')+' '+str(j.get('sub_field') or '')
    role=score_role(title,text)
    if not role:return None
    score,cat,why=role
    city=(j.get('location') or {}).get('city') or 'Germany'
    url=j.get('apply_url') or j.get('url')
    if not url:return None
    return dict(id='wsj-'+str(j.get('id')),title=title,company=(j.get('company') or {}).get('name') or 'Company not stated',
      city=city,location=city+', Germany',category=cat,employment='Internship',workplace=j.get('working_mode') or 'Not specified',
      posted=date_of(posted).isoformat(),url=url,detailsUrl=j.get('url') or url,score=score,
      reason='Estimated CV fit based on '+', '.join(why[:3])+'. Relevant to your UNU project coordination and Phitek operations work.',
      watchout='English/German fields provided by the board; review actual employer requirements and whether recent graduates may apply.',
      skills=j.get('skills') or [],source='workingstudentjobs.de (board date)',reviewed=False,deadline='',
      language='English required; German not required per board metadata',dateEvidence='Job-board posted_at or first_seen_at; employer-original date unverified')


def run():
    all_jobs=[];errors=[];scanned=0
    checks={'recent':0,'recent_germany':0,'matching_title':0,'english_evidence':0,'qualified_arbeitnow':0,'qualified_internships':0}
    url='https://www.arbeitnow.com/api/job-board-api?page=1'
    for page in range(1,11):
        if not url:break
        try:
            payload=fetch(url)
        except Exception as exc:
            errors.append('Arbeitnow page '+str(page)+': '+str(exc));break
        arr=payload.get('data') or []
        scanned+=len(arr)
        for x in arr:
            if recent(x.get('created_at')): checks['recent']+=1
            if not recent(x.get('created_at')) or not in_germany(x.get('location')): continue
            checks['recent_germany']+=1
            title=str(x.get('title') or '')
            if not TITLE_GOOD.search(title) or TITLE_BAD.search(title): continue
            checks['matching_title']+=1
            if not language_ok(clean(x.get('description')),x.get('tags') or ()):continue
            checks['english_evidence']+=1
            found=from_arbeitnow(x)
            if found: all_jobs.append(found);checks['qualified_arbeitnow']+=1
        if arr and all(j.get('created_at') and not recent(j['created_at']) and date_of(j['created_at']) is not None and date_of(j['created_at'])<MIN_DATE for j in arr):break
        next_url=(payload.get('links') or {}).get('next')
        url=urllib.parse.urljoin('https://www.arbeitnow.com',next_url) if next_url else None
    since=MIN_DATE.isoformat()
    url='https://www.workingstudentjobs.de/api/v1/jobs?'+urllib.parse.urlencode({
      'type':'internship','language':'en','since':since,'field':'operations,consulting,marketing,finance,research','limit':300,'ref':'jobpilot'})
    for page in range(2):
        if not url:break
        try:payload=fetch(url)
        except Exception as exc:
            errors.append('Internship feed: '+str(exc));break
        arr=payload.get('data') or []
        scanned+=len(arr)
        for x in arr:
            found=from_intern(x)
            if found: all_jobs.append(found);checks['qualified_internships']+=1
        next_url=(payload.get('links') or {}).get('next')
        url=urllib.parse.urljoin('https://www.workingstudentjobs.de',next_url) if next_url else None
    # Never count an old job simply because it was retained from a previous day's JSON.
    dedup={}
    for j in all_jobs:
        key=re.sub('[^a-z0-9]','',str(j['company']+'|'+j['title']).lower())
        if key not in dedup or j['score']>dedup[key]['score']:dedup[key]=j
    jobs=sorted(dedup.values(),key=lambda j:(-j['score'],j['posted']))
    meta=dict(generated_at=NOW.isoformat(),timezone='Europe/Berlin',scanned=scanned,added=len(jobs),errors=errors,
      source_note='Automatic 70+ CV-fit screening of seven role categories (project, operations, business analysis, strategy/consulting, product, programme, marketing/growth). Employer-original publication dates and mandatory language cannot be independently guaranteed.',
      search_window={'from':MIN_DATE.isoformat(),'to':TODAY.isoformat()},diagnostics=checks,jobs=jobs)
    # Never replace the prior feed with an empty success if all sources fail.
    if errors and scanned==0 and OUT.exists():
        previous=json.loads(OUT.read_text(encoding='utf-8'))
        if previous.get('jobs'):
            meta['jobs']=[j for j in previous['jobs'] if recent(j.get('posted'))]
            meta['added']=len(meta['jobs'])
            meta['source_note']+=' Latest sources failed; only still-recent previously fetched jobs retained.'
    OUT.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Generated {len(meta["jobs"])} jobs from {scanned} records, {len(errors)} source errors')
    print('Filter diagnostics:',checks)
    if errors:print('Warnings:',*errors,sep='\n  ')
    return 0

if __name__=='__main__':sys.exit(run())
