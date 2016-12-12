use strict;
use warnings;
use File::Copy qw(copy);
use Getopt::Long qw(GetOptions);

sub execute($) {
	my $cmd = shift;
	system($cmd);
	use Carp qw(croak);
	croak "\n\nError executing \n\t'$cmd'\n\n" if ( ( $? >> 8 ) != 0 || $? == -1 || ( $? & 127 ) != 0 );
}

my $njobs = 2;
GetOptions('njobs=i' => \$njobs) or exit;

my $header = qq(
OPT	+=  -DUNEQUALSOFTENINGS
OPT	+=  -DMULTIPLEDOMAINS=64
OPT	+=  -DTOPNODEFACTOR=3.0
OPT	+=  -DPEANOHILBERT
OPT	+=  -DWALLCLOCK
OPT	+=  -DMYSORT
OPT	+=  -DDOUBLEPRECISION
OPT	+=  -DNO_ISEND_IRECV_IN_DOMAIN
OPT	+=  -DFIX_PATHSCALE_MPI_STATUS_IGNORE_BUG
OPT	+=  -DOUTPUTPOTENTIAL
OPT	+=  -DHAVE_HDF5
);

sub build() {
	execute("cd src; make clean; make -j$njobs");
}

open my $fdOut, '>', 'src/gadget.make' or die;
print $fdOut $header;
close $fdOut;
build();
copy('src/Gadget3', 'nogas/') or die;
copy('src/Gadget3', 'gas/') or die;

