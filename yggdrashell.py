#!/usr/bin/env python

import yaml, sys, random, re, time

import math

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infile", metavar="INFILE", help="data file to read from")
parser.add_argument("outfile", metavar="OUTFILE", help="data file to write to", nargs="?")
parser.add_argument("-c", action="store_true", help="pritn census")
parser.add_argument("-e", metavar="EXPENSESFILE", help="expenses file to read")
parser.add_argument("-n", action="store_true", help="dry run/half-Tick (no worship, no population growth, no influence")
parser.add_argument("-s", metavar="SIGMA", help="percent uncertainty of population values {default:20}", type=float)
args = parser.parse_args()

DEBUG=0

SIGMA=.01 * 20
CENSUS = args.c

if type(args.s) is float:
	SIGMA = 0.01 * args.s

def yg_roll(x): 
	fpart = x - int(x)
	if random.random() < fpart: return int(x)+1
	else: return int(x)

def formula(x):
	return 2*math.log(1 + x, 2)

#attempt to load .ygconfig
try: 
	with open('.ygconfig') as f:
		try:
			cfg = yaml.load(f)
		except yaml.YAMLError as e:
			print(e)
			sys.exit(1)
except FileNotFoundError:
	print('Configuration file .ygconfig not found, attempting to create with YG4 entries', file=sys.stderr)
	with open('.ygconfig', 'w') as f:
		now = time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime())
		f.write('#Generated ' + now + '\n')
		f.write("godfields: ['gid', 'sphere', 'player', 'essence']\n")
		f.write("racefields: ['rid', 'pop', 'price', 'layer', 'location', 'crunch', 'tech', 'url']")
	f.close()
	with open('.ygconfig') as f:
		try:
			cfg = yaml.load(f)
		except yaml.YAMLError as e:
			print(e)
			sys.exit(1)
		if "census" in cfg.keys(): CENSUS = 1
		else: CENSUS = 0
	f.close()

godfields = cfg['godfields']
racefields = cfg['racefields']

#open base data
with open(args.infile) as stream:
	try:
		x = yaml.load(stream)
	except yaml.YAMLError as e: 
		print(e)
		sys.exit(1)
stream.close()

#open and perform deductions
#incomes = {}
expenses = {}

growths = {}
if args.e:
	fex = open(args.e)
	for l in fex:
		if re.match("^\s*#", l): continue
		if re.match("^\s*$", l): continue
		record = re.split("\s*:\s*", l.strip())
		deduction = float(re.findall("^[-+0-9]+", record[1])[0])
		
		deduction = yg_roll(deduction)
		x['gods'][record[0]]['essence'] += deduction

		try: expenses[record[0]] += min(0, deduction)
		except KeyError: expenses[record[0]] = min(0, deduction)
		#try: 
		#	x['gods'][record[0]]['essence'] += deduction
		#except KeyError: pass
	fex.close()

	if not args.n:
		if 'cap' in x['gods'][sorted(x['gods'].keys())[0]].keys(): 
			s = 0
			for g in sorted(x['gods'].keys()): s += x['gods'][g]['cap']
			mean = s/len(x['gods'])
			s = 0
			for g in sorted(x['gods'].keys()): s += (x['gods'][g]['cap'] - mean)**2
			stdev = (s/len(x['gods']))**.5
			for g in sorted(x['gods'].keys()): 
				growths[g] = 0
				#calculate cap increases
				#component 1: 50%, rewards being at low Essence total
				growths[g] += max(0, 1/2*(16/(x['gods'][g]['essence'] + 3)**2))
				#component 2: 35%, rewards spending high proportionate Essence
				growths[g] += max(0, 1/3*x['gods'][g]['essence']/x['gods'][g]['cap'])
				#component 3: 20%, rewards having a lower-than-average cap`
				growths[g] += max(0, 1/10*max(-(x['gods'][g]['cap'] - mean)/mean, 0))
			for g in sorted(x['gods'].keys()):
				x['gods'][g]['cap'] += yg_roll(growths[g])

#worship calcs
worships = {}
for r in sorted(x['races'].keys()): 
	for g in sorted(x['races'][r]['worships'].keys()):

		p = x['races'][r]['pop'] 

		if type(p) is list: p = sum(p)

		try: 
			worships[g] += p * x['races'][r]['worships'][g]
		except KeyError: worships[g] = p * x['races'][r]['worships'][g]

if not args.n:
	for g in sorted(worships.keys()):
		try: i = x['influence']['to'][g] * x['influence']['pop']
		except KeyError: i = 0
		w = yg_roll(formula(worships[g]+i))
		#if DEBUG: print("w = %0.2f, i = %0.2f, E/t = %0.2f to %s" % (worships[g], i, formula(worships[g]+i), g))
		if DEBUG: print("%s +%0.fE" % (g, formula(worships[g]+i)))
		if 'cap' in x['gods'][g].keys():
			if x['gods'][g]['essence'] > 0: x['gods'][g]['essence'] = min(x['gods'][g]['essence'] + w, x['gods'][g]['cap'])
		else:
			if x['gods'][g]['essence'] > 0: x['gods'][g]['essence'] += w

#influence
def deprecatedinfluence():
	print("pop\tworship\tspent\tinfl\tinflinc\tgod")
	if not args.n:
		for g in sorted(x['gods']):
			inftest = ""
			try:
				w = worships[g]
			except KeyError:
				w = 0
			try: i = x['influence']['worships'][g]
			except KeyError: i = 0
			def infi(inf, wor): return 1000*inf/(wor**4 + 0.001)
			print(round(w), "\t", round(formula(w)), "\t", round(i), "\t", round(infi(i, w)), "\t", round(formula(infi(i, w))), "\t", g)

#sort by gid
names = []
gids = []
for g in sorted(x['gods'].keys()):
	names.append(g)
	gids.append(x['gods'][g]['gid'])

#print
print('[spoiler=Deities('+str(len(gids))+')]')
fg = dict(zip(gids, names))
for i in sorted(fg.keys()):
	g = x['gods'][fg[i]]
	#print(fg[i],'('+g['sphere']+')',str(g['essence'])+'E')

	if 'cap' in x['gods'][fg[i]].keys(): print('%s (%s) %d/%dE' % (fg[i], g['sphere'], g['essence'], g['cap']))
	else: print('%s (%s) %dE' % (fg[i], g['sphere'], g['essence']))
print('[/spoiler]')

if CENSUS:
	print()
	print('[spoiler=Worship-forming units (plus/minus '+str(SIGMA*100)+'%)]')
	for i in sorted(fg.keys()):
		try: n = worships[fg[i]]
		except KeyError: n = 0
		print(fg[i], round(abs(n + random.gauss(0, SIGMA*n))))
	print('[/spoiler]')

#deductions first in the future

#breed the races

for r in sorted(x['races'].keys()):
	if type(x['races'][r]['pop']) is list:
		for n in range(len(x['races'][r]['pop'])):
			x['races'][r]['pop'][n] *= (1 + .06 - .02)
	else: x['races'][r]['pop'] *= (1 + .06 - .02)

#sort races by rid
names = []
gids = []
for g in sorted(x['races'].keys()):
	names.append(g)
	gids.append(x['races'][g]['rid'])

fr = dict(zip(gids, names))
#for i in sorted(fg.keys()):

#save gods
s = ''
t = '    '
s += 'gods:\n'

for g in sorted(fg.keys()):
	s += t+fg[g]+':\n'
	for prop in godfields:
		s += 2*t + prop + ': ' + str(x['gods'][fg[g]][prop]) + '\n'

#save influence
if 'influence' in x.keys():
	s += 'influence:\n'
	s += t + 'pop: ' + str(x['influence']['pop']) + '\n'
	s += t + 'to:\n'

	for g in sorted(x['influence']['to']):
		s += 2*t + g + ': ' + str(x['influence']['to'][g]) + '\n'

#save races

s += 'races:\n'

for r in sorted(fr.keys()):
	s += t+fr[r]+':\n'
	for prop in racefields:
		if prop == "description":
			try: 
				desc = re.sub('\n', '\\\\n', x['races'][fr[r]][prop])
				desc = re.sub('"', '\\"', desc)
				desc = '"' + desc + '"'
				s += 2*t + prop + ': ' + desc + '\n'
			except KeyError: pass
			continue
		try: s += 2*t + prop + ': ' + str(x['races'][fr[r]][prop]) + '\n'
		except KeyError: pass

	s += 2*t + 'worships: \n'
	for g in x['races'][fr[r]]['worships']:
		s += 3*t + g + ': ' + str(x['races'][fr[r]]['worships'][g]) + '\n'
try:
	f = open(args.outfile, 'w')
	f.write(s.strip())
	f.close()
	f = open('.' + args.outfile, 'w')
	f.write(s.strip())
	f.close()
except TypeError: pass
