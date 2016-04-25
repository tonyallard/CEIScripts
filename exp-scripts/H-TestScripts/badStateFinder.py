f = open("2015-12-04_11-41-49-DataFile.plt", 'r')

for x in f:
	if (x is "\n"):
		print "here lines"
		continue
	lines = x.split('\t')
	if (len(lines) < 2):
		continue
	hVal = float(lines[1].rstrip())
	if (hVal <= 0.005):
		print x


f.close()

