SHELL := /bin/bash # use base syntax
.PHONY: clean all

all: CDER.sys.score PER.sys.score TER.sys.score WER.sys.score sentence-BLEU.seg.score mteval-inter.sys.score

# warning: spaces around = in Makefiles are dangerous and spaces at the end of
# variable values are deadly
MOSESROOT?=/Users/qingsongma/Documents/tools/mosesdecoder-master
TOKENIZER=$(MOSESROOT)/scripts/tokenizer/tokenizer.perl
TOKENIZER_FLAGS?=" -threads 5 "
  # warning, multithreaded perl may not work on all setups

#CHRFROOT?=/lnet/spec/work/people/bojar/diplomka/granty/qt21/mtmetrics-qt21-svnserver/trunk/wmt18-metrics-task/chrf-debugging/chrF
CHRFROOT?=.
sacreBLEUROOT?=/Users/qingsongma/Documents/tools/sacreBLEU-master

DATAFILE?=../input/wmt19-submitted-data-v3-txt-minimal.tar
year?=2019

input:
	mkdir input
	tar -xvzf $(DATAFILE) -C input

data: input
	mkdir data
	mkdir -p data/references
	mkdir -p data/sources
	mkdir -p data/system-outputs
	cp input/wmt19-submitted-data-v3/txt/references/* data/references
	cp input/wmt19-submitted-data-v3/txt/sources/* data/sources
	cp -r input/wmt19-submitted-data-v3/txt/system-outputs/* data/system-outputs

tokenized:
	[ -x "$(TOKENIZER)" ]  ## testing for existence of tokenizer (i.e. MOSESROOT)
	for sysoutput in data/system-outputs/newstest${year}/*/* data/references/*; do \
		basename=$$(basename $$sysoutput); \
		direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
		ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		dirname=$$(dirname $$sysoutput); \
		newdir=$$(echo $$dirname | sed "s|^data|tokenized|"); \
                mkdir -p $$newdir; \
		if [ $$ext = zh ]; then \
			python2.7 tokenizeChinese.py $$sysoutput $$newdir/$$basename; \
		else \
			cat $$sysoutput | $(TOKENIZER) -l $$ext $(TOKENIZER_FLAGS) | perl -pe '$$_= lc($$_)' > $$newdir/$$basename ; \
		fi; \
		echo $$sysoutput, $$newdir;\
	done

# Set the following two variables empty for serial execution:
SUBMIT_JOB_PREFIX?=sbatch -n 1 -o mteval-inter.out --wrap="
SUBMIT_JOB_SUFFIX?="
# get scores for all metrics using moses scorer
%.sys:
	metric=$*; \
	mkdir $$metric.sys; \
	for system in tokenized/system-outputs/*/*/*; do \
	        basename=$$(basename $$system); \
	        testset=$$(echo $$basename | cut -d. -f1); \
	        systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
	        directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
	        direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
	        ext=$$(echo $$direction | fold -w2 | tail -n 1); \
	        reference="tokenized/references/$$testset-$$direction-ref.$$ext"; \
	        #$(SUBMIT_JOB_PREFIX)$(MOSESROOT)/mert/evaluator --sctype $$metric --reference $$reference --candidate $$system > $$metric.sys/$$directionwithdash.$$testset.$$systemname$(SUBMIT_JOB_SUFFIX); 
	        $(MOSESROOT)/mert/evaluator --sctype $$metric --reference $$reference --candidate $$system > $$metric.sys/$$directionwithdash.$$testset.$$systemname; \
	        echo $$metric, $$reference, $$system, $$directionwithdash, $$testset, $$systemname; \
	        echo $$basename, $$testset, $$direction, $$ext; \
	done

sentence-BLEU.seg.score:
	for system in tokenized/system-outputs/*/*/*; do \
		if [[ $$system =~ .hybrid. ]]; then continue; fi; \
		metric=sentBLEU; \
                basename=$$(basename $$system); \
                testset=$$(echo $$basename | cut -d. -f1); \
                systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
                direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
                ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="tokenized/references/$$testset-$$direction-ref.$$ext"; \
		i=1; \
		cat $$system | $(MOSESROOT)/mert/sentence-bleu $$reference | while read score; do \
			echo $$metric $$directionwithdash $$testset $$systemname $$i $$score | tr " " "\t"; \
			i=$$(($$i+1)); \
		done; \
	done > $@
	gzip $@

mteval-inter:
	# creates a launcher for evaluating mteval
	mkdir mteval-inter
	for system in tokenized/system-outputs/newstest$(year)/*/*; do \
		basename=$$(basename $$system); \
                testset=$$(echo $$basename | cut -d. -f1); \
                systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
		direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
        ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="tokenized/references/$$testset-$$direction-ref.$$ext"; \
		cat $$system | ./wrapmteval.pl --international-tokenization --fake-source $$reference > mteval-inter/$$directionwithdash.$$testset.$$systemname.mtevalout;\
		echo $$reference, $$system, $$directionwithdash, $$testset, $$systemname; \
		echo $$basename, $$testset, $$direction, $$ext; \
	done 

mteval.sys.score:
	for system in mteval-inter/*; do \
		basename=$$(basename $$system); \
		directionwithdash=$$(echo $$basename | cut -d. -f1); \
		testset=$$(echo $$basename | cut -d. -f2); \
		systemname=$$(echo $$basename | cut -d. -f3- | rev | cut -d. -f2- | rev ); \
		NIST=$$(cat $$system | grep "for system" | sed "s/ \+/\t/g" | cut -f4); \
		BLEU=$$(cat $$system | grep "for system" | sed "s/ \+/\t/g" | cut -f8); \
		echo NIST $$directionwithdash $$testset $$systemname $$NIST | tr " " "\t"; \
		echo BLEU $$directionwithdash $$testset $$systemname $$BLEU | tr " " "\t"; \
	done > $@
	gzip $@


chrF:
	mkdir chrF
	for system in data/system-outputs/newstest${year}/*/*; do \
	        basename=$$(basename "$$system"); \
	        testset=$$(echo "$$basename" | cut -d. -f1); \
	        systemname=$$(echo "$$basename" | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
	        directionwithdash=$$(echo "$$basename" | rev | cut -d. -f1 | rev); \
	        direction=$$(echo "$$basename" | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
	        ext=$$(echo "$$direction" | fold -w2 | tail -n 1); \
	        reference="data/references/$$testset-$$direction-ref.$$ext"; \
	        $(CHRFROOT)/chrF++.py -R $$reference -H $$system -nw 0 -b 3 -s > chrF/$$directionwithdash.$$testset.$$systemname; \
	        echo $$reference, $$system, $$directionwithdash, $$testset, $$systemname; \
	        echo $$basename, $$testset, $$direction, $$ext; \
	done

nw1-chrF:
	mkdir chrF+
	for system in data/system-outputs/newstest${year}/*/*; do \
		basename=$$(basename $$system); \
                testset=$$(echo $$basename | cut -d. -f1); \
                systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
		direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
        ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="data/references/$$testset-$$direction-ref.$$ext"; \
		python chrF++.py -R $$reference -H $$system -nw 1 -b 3 -s > chrF+/$$directionwithdash.$$testset.$$systemname; \
		echo $$reference, $$system, $$directionwithdash, $$testset, $$systemname; \
		echo $$basename, $$testset, $$direction, $$ext; \
	done

sacreBLEU-BLEU:
	mkdir sacreBLEU-BLEU.sys
	for system in data/system-outputs/newstest$(year)/*/*; do \
		basename=$$(basename $$system); \
                testset=$$(echo $$basename | cut -d. -f1); \
                systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
		direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g' ); \
        ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="data/references/$$testset-$$direction-ref.$$ext"; \
		python3 $(sacreBLEUROOT)/sacrebleu.py -l $$directionwithdash -i $$system -refs $$reference -m bleu -lc -tok intl -b -w 4 > sacreBLEU-BLEU.sys/$$directionwithdash.$$testset.$$systemname; \
		echo $$reference, $$system, $$directionwithdash, $$testset, $$systemname; \
		echo $$basename, $$testset, $$direction, $$ext; \
	done

sacreBLEU-chrF:
	mkdir sacreBLEU-chrF.sys
	for system in data/system-outputs/newstest2019/*/*; do \
		basename=$$(basename $$system); \
                testset=$$(echo $$basename | cut -d. -f1); \
                systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
		direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g' ); \
        ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="data/references/$$testset-$$direction-ref.$$ext"; \
		python3 $(sacreBLEUROOT)/sacrebleu.py -l $$directionwithdash -i $$system -refs $$reference -m chrf --chrf-order 6 --chrf-beta 3 -b -w 4 > sacreBLEU-chrF.sys/$$directionwithdash.$$testset.$$systemname; \
		echo $$reference, $$system, $$directionwithdash, $$testset, $$systemname; \
		echo $$basename, $$testset, $$direction, $$ext; \
	done


%.sys.score:
	for system in $*.sys/*; do \
		basename=$$(basename $$system); \
		directionwithdash=$$(echo $$basename | cut -d. -f1); \
		testset=$$(echo $$basename | cut -d. -f2); \
		systemname=$$(echo $$basename | cut -d. -f3- | rev | cut -d. -f1- | rev ); \
		SCORE=$$(cat $$system); \
		echo $* $$directionwithdash $$testset $$systemname $$SEG $$SCORE | tr " " "\t"; \
	done > $@
	gzip $@


mteval-inter-2.sys.score:
	for system in data/system-outputs/*/*/*; do \
		basename=$$(basename $$system); \
                testset=$$(echo $$basename | cut -d. -f1); \
                systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
                direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
                ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="tokenized/references/$$testset-$$direction-ref.$$ext"; \
		cat $$system \
			| ./wrapmteval.pl --international-tokenization --fake-source $$reference \
		   	| grep "for system" \
			> tmp; \
		NIST=$$(cat tmp | sed "s/  */	/g" | cut -f4); \
		BLEU=$$(cat tmp | sed "s/  */	/g" | cut -f8); \
		echo NIST $$directionwithdash $$testset $$systemname $$NIST | tr " " "\t"; \
		echo BLEU $$directionwithdash $$testset $$systemname $$BLEU | tr " " "\t"; \
		rm tmp; \
	done > $@
	gzip $@


CharacTER-score:
	mkdir CharacTER-score
	for system in tokenized/system-outputs/*/*/*; do \
		echo "$$system" >&2 ; \
		basename=$$(basename $$system); \
		testset=$$(echo $$basename | cut -d. -f1); \
		systemname=$$(echo $$basename | cut -d. -f2- | rev | cut -d. -f2- | rev ); \
		directionwithdash=$$(echo $$basename | rev | cut -d. -f1 | rev); \
		direction=$$(echo $$basename | rev | cut -d. -f1 | rev | sed -e 's/-//g'); \
		ext=$$(echo $$direction | fold -w2 | tail -n 1); \
		reference="tokenized/references/$$testset-$$direction-ref.$$ext"; \
		sbatch -n 1 -o characTER.out --wrap="python2 CharacTER.py -v -r $$reference -o $$system > CharacTER-score/$$directionwithdash.$$testset.$$systemname"; \
	done
clean:
	rm -rf tokenized *.score.gz
