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

my ($charm, $changa, $clean, $smp, $njobs ) = ( 1, 1, 0 , 1, 2);
GetOptions(
	'charm!'    => \$charm,
	'changa!'   => \$changa,
	'clean'     => \$clean,
	'smp!'		=> \$smp,
	'njobs=i'	=> \$njobs
) or exit;
$smp  = ($smp) ? 'smp' : '';

if ($charm) {
	if ($clean) {
		print("Cleaning charm...\n");
		execute( "
			cd src/charm
			rm -rf bin include lib lib_so tmp VERSION net-linux*
		" );
	}
	execute( "
		cd src/charm
		./build ChaNGa net-linux-x86_64 $smp --enable-lbuserdata -j$njobs -optimize
	" );
}

if ($changa) {
	if ($clean) {
		print("Cleaning changa...\n");
		execute( "
			cd src/changa
			rm -f *.a *.o config.status Makefile.dep Makefile cuda.mk ChaNGa charmrun
		" );
	}
	
	execute("cd src/changa; ./configure; make depends; make -j$njobs");
	copy('src/changa/ChaNGa', 'nogas/') or die;
	copy('src/changa/ChaNGa', 'gas/') or die;
}
