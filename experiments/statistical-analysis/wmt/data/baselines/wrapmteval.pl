#!/usr/bin/perl
# This is a script that runs NIST mteval on (a subset of) a test set.
# All necessary files are created in a temp dir.
# This wrapper also forces --international-tokenization for mteval.

use strict;
use Getopt::Long;
use File::Path;
use File::Basename;
use File::Temp qw(tempdir);
use File::Spec;

binmode(STDIN, ":utf8");
binmode(STDOUT, ":utf8");
binmode(STDERR, ":utf8");

my $mteval = File::Spec->catfile(dirname(File::Spec->rel2abs(__FILE__)),
                    "mteval-v13a.pl");

my $setid = "SETID";
my $docid = "DOCID";
my $srclang = "slang";
my $tgtlang = "tlang";

my $tmpdir = "/mnt/h/tmp";
$tmpdir = "/tmp" if ! -e $tmpdir;
my $keep = 0;
my $fake_source = 0;
my $restrict = 0;
my $srcfile = undef;
my $hypnames = undef;
my $international_tokenization = 0;
GetOptions(
  "tempdir=s" => \$tmpdir,
  "keep" => \$keep,
  "fake-source" => \$fake_source,
  "restrict-to-the-given-sentences" => \$restrict,
  'international-tokenization' => \$international_tokenization,
  "hypnames=s" => \$hypnames,
) or exit 1;

my $reffile = shift;
my $hypfile = shift;

if (!defined $reffile) {
  print STDERR "usage: $0 referencesfile < hypfile
   or: $0 referencesfile.gz hypfile.gz
If you have more references, use:
  $0 <(paste ref1 ref2) < hypfile
Options:
--restrict-to-the-given-sentences
   ... the first column of the references file gives line numbers
       (indexed from 1) that we need out hypothesis to be restricted to
       Repeated lines *are* allowed.
--fake-source ... use the hypothesis file as the source; mteval does not use it
              anyway
--source=fname ... the source sentences [not implementened]
--keep ... do not delete the temp dir with the SGML files
--hypnames='systemA systemB' ... the hypfile is expected to have this many cols
";
  exit 1;
}

die "Not an executable: $mteval" if ! -x $mteval;

die "Please use --fake-source to use the hypothesis as a dummy source."
  if !$fake_source && !defined $srcfile;

my $tempdir = tempdir("$tmpdir/wrapmteval.XXXXX", CLEANUP=>!$keep);
print STDERR "Will preserve tempdir: $tempdir\n"
  if $keep;

if (defined $hypnames) {
  $hypnames = [ split /\s+/, $hypnames ];
}

# read the hypothesis/ses
if (!defined $hypfile) {
  $hypfile = "-";
  print STDERR "Reading stdin...\n";
}
my @hypdata = ();
my $hypcount = (defined $hypnames ? scalar(@$hypnames) : undef);
my $tmph = my_open($hypfile);
my $nr = 0;
while (<$tmph>) {
  $nr++;
  chomp;
  my @cols = split /\t/;
  if (defined $hypcount) {
    die "$hypfile:$nr:Mismatched number of hypotheses, got "
      .scalar(@cols). ", expected $hypcount"
      if $hypcount != scalar(@cols);
  } else {
    $hypcount = scalar(@cols);
  }
  push @hypdata, [map { trim($_) } @cols];
}
$hypcount = 1 if !defined $hypcount;
print STDERR "Stored ".scalar(@hypdata)." lines of"
  .($hypcount>1 ? " $hypcount hypotheses" : " the hypothesis")
  ."\n";
close $tmph if $hypfile ne "-";

# read references
my $use_sentids = $restrict ? [] : undef;
my @refdata = ();
$tmph = my_open($reffile);
# read input, copy to file
my $nr = 0;
my $refcount = undef;
while (<$tmph>) {
  chomp;
  my @cols = split /\t/;
  if ($restrict) {
    my $sentid = shift @cols;
    die "$reffile:$nr:Missed sentence id" if !defined $sentid;
    die "$reffile:$nr:Bad sentence id '$sentid'" if $sentid !~ /^[0-9]+$/;
    push @$use_sentids, $sentid;
  }
  if (defined $refcount) {
    die "$reffile:$nr:Mismatched number of references, got "
      .scalar(@cols). ", expected $refcount"
      if $refcount != scalar(@cols);
  } else {
    $refcount = scalar(@cols);
  }
  push @refdata, [map { trim($_) } @cols];
}
print STDERR "Stored ".scalar(@refdata)." lines of $refcount references.\n";
close $tmph if $reffile ne "-";

if ($restrict) {
  print STDERR "Restricting the hypothesis to ".scalar(@$use_sentids)
    ." sentences.\n";
  my @usehypdata = ();
  foreach my $sentid (@$use_sentids) {
    push @usehypdata, $hypdata[$sentid];
  }
  @hypdata = @usehypdata;
}

my $refsgml = "$tempdir/reference.sgml";
my $hypsgml = "$tempdir/hypothesis.sgml";
my $srcsgml = "$tempdir/source.sgml";
emit_sgml("refset", $refsgml, \@refdata, $refcount);
emit_sgml("tstset", $hypsgml, \@hypdata, $hypcount, $hypnames);
if ($fake_source) {
  emit_sgml("srcset", $srcsgml, \@hypdata, 1);
}

if ($international_tokenization) {
    safesystem($mteval, "--international-tokenization", "-r", $refsgml, "-s", $srcsgml, "-t", $hypsgml) or die;
} else {
    safesystem($mteval, "-r", $refsgml, "-s", $srcsgml, "-t", $hypsgml) or die;
}
# 
# unlink($reffile); unlink($srcfile); unlink($hypfile);


# save the hypothesis
sub emit_sgml {
  my $type = shift;
  my $outfn = shift;
  my $outarray = shift;
  my $outcolcount = shift; # set to zero if @$outarray are directly the string
  my $sysnames = shift; # undef or exactly $outcolcount items

  print STDERR "Preparing $outfn"
    .($outcolcount ? " with $outcolcount variants" : "")."\n";
  my $outh = my_save($outfn);
  if (0 < $outcolcount) {
    foreach my $col (0..$outcolcount-1) {
      my $sysname = $outfn.".$col";
      $sysname = $sysnames->[$col] if defined $sysnames;
      emit_column($sysname, $outh, $type, $outarray, $col);
    }
  } else {
    emit_column($outfn, $outh, $type, $outarray, undef);
  }
  close $outh;
}

sub emit_column {
  my $sysname = shift;
  my $outh = shift;
  my $type = shift;
  my $outarray = shift;
  my $outcol = shift; # set to undef if @$outarray are directly the string

  print $outh "<$type setid=\"$setid\" srclang=\"$srclang\" trglang=\"$tgtlang\">\n";
  print $outh "<DOC docid=\"$docid\" sysid=\"$sysname\">\n";
  my $nr = 0;
  foreach my $line (@$outarray) {
    $nr++;
    # print STDERR "$type: column $outcol, line $nr: $line\n";
    my $text;
    if (defined $outcol) {
      $text = $line->[$outcol];
    } else {
      $text = $line;
    }
    print $outh "<seg id=\"$nr\">$text</seg>\n";
  }
  print $outh "</DOC>\n";
  print $outh "</$type>\n";
}


sub safesystem {
  print STDERR "Executing: @_\n";
  system(@_);
  if ($? == -1) {
      print STDERR "Failed to execute: @_\n  $!\n";
      exit(1);
  }
  elsif ($? & 127) {
      printf STDERR "Execution of: @_\n  died with signal %d, %s coredump\n",
          ($? & 127),  ($? & 128) ? 'with' : 'without';
      exit(1);
  }
  else {
    my $exitcode = $? >> 8;
    print STDERR "Exit code: $exitcode\n" if $exitcode;
    return ! $exitcode;
  }
}

sub my_open {
  my $f = shift;
  if ($f eq "-") {
    binmode(STDIN, ":utf8");
    return *STDIN;
  }

  die "Not found: $f" if ! -e $f;

  my $opn;
  my $hdl;
  my $ft = `file '$f'`;
  # file might not recognize some files!
  if ($f =~ /\.gz$/ || $ft =~ /gzip compressed data/) {
    $opn = "zcat '$f' |";
  } elsif ($f =~ /\.bz2$/ || $ft =~ /bzip2 compressed data/) {
    $opn = "bzcat '$f' |";
  } else {
    $opn = "$f";
  }
  open $hdl, $opn or die "Can't open '$opn': $!";
  binmode $hdl, ":utf8";
  return $hdl;
}

sub my_save {
  my $f = shift;
  if ($f eq "-") {
    binmode(STDOUT, ":utf8");
    return *STDOUT;
  }

  my $opn;
  my $hdl;
  # file might not recognize some files!
  if ($f =~ /\.gz$/) {
    $opn = "| gzip -c > '$f'";
  } elsif ($f =~ /\.bz2$/) {
    $opn = "| bzip2 > '$f'";
  } else {
    $opn = ">$f";
  }
  mkpath( dirname($f) );
  open $hdl, $opn or die "Can't write to '$opn': $!";
  binmode $hdl, ":utf8";
  return $hdl;
}

sub trim {
  my $text = shift;
  $text =~ s/^\s+|\s+$//g;
  $text =~ s/\s+/ /g;
  return $text;
}
