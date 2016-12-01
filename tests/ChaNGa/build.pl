use strict;
use warnings;
use Getopt::Long qw(GetOptions);

sub execute($) {
	my $cmd = shift;
	system($cmd);
	use Carp qw(croak);
	croak "\n\nError executing \n\t'$cmd'\n\n" if ( ( $? >> 8 ) != 0 || $? == -1 || ( $? & 127 ) != 0 );
}

my ($charm, $changa, $clean, $smp, $njobs ) = ( 1, 1, 0 , 1, 2);
GetOptions(
	'charm!'    => \$charm,
	'changa!'   => \$changa,
	'clean'     => \$clean,
	'smp!'		=> \$smp,
	'njobs=i'	=> \$njobs
) or exit;
$smp  = ($smp) ? 'smp' : '';

if ($clean) {
	execute( "
		cd charm
		rm -rf bin include lib lib_so tmp VERSION net-linux*
	" );
	execute( "
		cd changa
		rm -f *.a *.o config.status Makefile.dep Makefile cuda.mk ChaNGa charmrun
	" );
}
if ($charm) {
	execute( "
		cd charm
		./build ChaNGa net-linux-x86_64 $smp --enable-lbuserdata -j$njobs -optimize
	" );
}

if ($changa) {
	execute( "
		cd changa
		./configure
		make -j$njobs
	" );
}
