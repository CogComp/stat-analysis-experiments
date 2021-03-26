import gzip
import re
import sys
import glob
from bs4 import BeautifulSoup


print('Reading in the text metrics data...')
lps = r'..-[^g].'      #ESIM
lps = r'en-((de)|(ru))'      #USFD
lps = r'..-en'      #WMDO
lps = r'..-..'      #BEER
lps = r'..-en'      #bertr
lps = r'(en-((de)|(ru)))|(((de)|(ru))-en)'      #LP + LASIM

tally = {}
docids = {}
for fn in glob.glob('final-metric-scores/submissions-corrected/wmt19-submitted-data-v3/txt-ts/system-outputs/newstest2019/*/*'):
    basename = fn.split('/')[-1]
    
    attrs = basename.split('.')
    test_set, lp = attrs[0], attrs[-1]
    system = '.'.join(attrs[1:-1])
    #system = attrs[1]          # need to ask ondrej

    if re.match(lps, attrs[-1]) is None:
        continue
    print('Reading %s' % basename)

    for i, line in enumerate(open(fn, 'rt'), 1):
        tally[(lp, test_set, system, i)] = False

    fns = fn.split('/')
    sgm_ts = open('final-metric-scores/submissions-corrected/wmt19-submitted-data-v3/sgm-ts/system-outputs/newstest2019/%s/%s.sgm' % (fns[-2], fns[-1]), 'rt')
    soup = BeautifulSoup(sgm_ts.read())

    for j, (line, sgm_seg) in enumerate(zip(open(fn, 'rt'), soup.find_all('seg')), 1):
        docids[(lp, test_set, system, j)] = sgm_seg.parent.parent['docid']

    del(soup)

    if j != i:
        print(j, i)
        print('lines not aligned')
        exit()

    seg = sgm_seg.string
    if seg.strip() != line.strip():
        print(line.strip())
        print(seg.strip())
        print('sgm is not aligned with txt')
        print(fn)
        exit()
    
out = open(sys.argv[2], 'wt')

print('Validating...')
extra = set()
for i, row in enumerate(gzip.open(sys.argv[1], 'rt'), 1):
    # check for number of columns in row
    tabs = row.count('\t')
    if not tabs == 7:
        print('Line %d: %d of columns instead of 6' % (i, tabs))
        print(row)
        exit()

    # row to list
    row = row.split('\t')

    metric, lp, test_set, system, seg_num_str, score_str, ensemble, avail = tuple(row)
    if '+' in test_set:
        test_set = test_set[test_set.index('+')+1:]
    #system = system.split('.')[0]

    # check metric name and file name match
    if metric not in sys.argv[1]:
        #print('Line %d: file is not named with %s' % (i, metric))
        pass

    # check language pair is actually language pair
    if not len(lp) == 5 or not lp[2] == '-':
        print('Line %d: "%s" is bad language pair' % (i, lp))

    # check segment score is a float
    try:
        float(score_str)
    except:
        print('Line %d: "%s" is not a float score' % (i, score_str))

    #check ensemble
    if not ensemble == 'ensemble' and not ensemble == 'non-ensemble':
        if False:
            print('Line %d: "%s" is not a valid ensemble attribute' % (i, ensemble))

    key = (lp, test_set, system, int(seg_num_str))
    docid = docids[key]

    out_row = [ 'LP', lp, test_set.split('+')[-1], docid, system, seg_num_str, score_str, 'non-ensemble', 'not-public' ]
    out.write('%s\n' % '\t'.join(out_row))

    # check avail
    # maybe we can skip this

    # check for counts
    if key not in tally:
        print(key)
        print('Line %d: "%s" contains non-existant test instance' % (i,str(row)))
        extra.add((lp, test_set, system))
    elif not tally[key]:
        tally[key] = True
    else:
        print('Line %d: duplicate test instance' % i)
        extra.add((lp, test_set, system))
print('Extra submissions are: %s' % '\n\t'.join(str(t) for t in sorted(list(extra))))

# check if missing instances
print('Checking for missing instances...')
missing = set()
for key, value in sorted(tally.items()):
    if not value:
        if 'testsuite' not in docids[key]:
            print('There is no input for test instance %s' % str(key))
            missing.add(key[:-1])
        else:
            print('Missing testsuite instance %s' % str(key))

print(sorted(list(missing)))
print('Missing submissions are: %s' % '\n\t'.join(str(t) for t in sorted(list(missing))))
