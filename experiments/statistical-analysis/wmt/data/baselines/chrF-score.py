import glob
import gzip
import sys
import os

met=sys.argv[1]
#outD='./chrF-process/'
outD='./'

def getSysScore(inf):
    #./chrF/en-tr.newstest2018.hybrid.1043
    name=inf.split('/')[-1]
    pp = name.split('.')
    lan, data = pp[0], pp[1]
    sysname = '.'.join(pp[2:])
	
    lines = [line for line in open(inf)]
    if '-avgF3' in lines[-2]: # macro-averaged 
	sysscore = lines[-2].strip().split()[1]
	
    for i in range(1,len(lines)-3):
	pp = lines[i].rstrip().split("\t")
	idx = pp[0].split("::")[0]
	segscore = pp[1]	
	print met+"\t"+lan+"\t"+data+"\t"+sysname+"\t"+idx+"\t"+segscore

    return met+"\t"+lan+"\t"+data+"\t"+sysname+"\t"+sysscore+"\n"

if __name__=='__main__':
    if not os.path.exists(outD):
	os.makedirs(outD)
    
    o = gzip.open(outD+met+'.sys.score.gz', 'wb')
    for inf in glob.glob(met+'/*'):
	line = getSysScore(inf)
	o.write(line)
    o.close()
