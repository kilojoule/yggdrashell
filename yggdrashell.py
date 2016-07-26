#!/usr/bin/env python

import yaml, sys, random, re

import math

godfields = ['gid', 'sphere', 'player', 'essence']
racefields = ['rid', 'pop', 'price', 'layer', 'location', 'crunch', 'tech', 'ur']

#attempt to load .ygconfig
with open('.ygconfig') as f:
	try:
		cfg = yaml.load(f)
	except yaml.YAMLError as e:
		print(e)
		sys.exit(1)
godfields = cfg['godfields']
racefields = cfg['racefields']


def yg_roll(x): 
	fpart = x - int(x)
	if random.random() < fpart: return int(x)+1
	else: return int(x)

#open base data
with open(sys.argv[1]) as stream:
	try:
		x = yaml.load(stream)
	except yaml.YAMLError as e: 
		print(e)
		sys.exit(1)

#open deductions

#worship calcs
worships = {}
for r in sorted(x['races'].keys()): 
	#print(r)
	#print('\tPop:',x['races'][r]['pop'])	
	#print('\tWorships:',x['races'][r]['worships'])

	for g in sorted(x['races'][r]['worships'].keys()):
		

		p = x['races'][r]['pop'] 

		if type(p) is list: p = sum(p)

		try: worships[g] += p * x['races'][r]['worships'][g]
		except KeyError: worships[g] = p

for g in sorted(worships.keys()):
	w = yg_roll(2*math.log(1+worships[g], 2))
	x['gods'][g]['essence'] += w

#sort by gid
names = []
gids = []
for g in sorted(x['gods'].keys()):
	names.append(g)
	gids.append(x['gods'][g]['gid'])

fg = dict(zip(gids, names))
for i in sorted(fg.keys()):
	g = x['gods'][fg[i]]
	print(fg[i],'('+g['sphere']+')',str(g['essence'])+'E')

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

#save races

s += 'races:\n'

for r in sorted(fr.keys()):
	s += t+fr[r]+':\n'
	for prop in racefields:
		try: s += 2*t + prop + ': ' + str(x['races'][fr[r]][prop]) + '\n'
		except KeyError: pass

	s += 2*t + 'worships: \n'
	for g in x['races'][fr[r]]['worships']:
		s += 3*t + g + ': ' + str(x['races'][fr[r]]['worships'][g]) + '\n'

try:
	f = open(sys.argv[2], 'w')
	f.write(s.strip())
	f.close()
except IndexError: pass
