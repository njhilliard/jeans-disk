use strict;
use warnings;
use File::Path qw(mkpath);
use Cwd qw(cwd);

my $base_dir = cwd();

my $sim_time 	  = 0.500;	# 500 Myrs
my $max_step 	  = 0.001;	# 1   Myr
my $snap_interval = 0.050;	# 50  Myrs

for my $type ('gas', 'nogas') {
	my $dir = "$base_dir/$type";
	mkpath($dir) if (! -d $dir);
	
	open my $fdOut, '>', "$dir/${type}.params" or die "Unable to create $dir/${type}.params: $!\n";
	print $fdOut <<EOF
InitCondFile		$dir/$type
SnapshotFileBase	$type
OutputDir			$dir
TimeMax				$sim_time
CoolingOn			0
StarformationOn		0
TimeBetSnapshot		$snap_interval
TimeOfFirstSnapshot	$snap_interval
MaxSizeTimestep		$max_step
EOF
;

	open my $fdIn, '<', "$base_dir/params.template" or die "Unable to open $base_dir/params.template: $!\n";
	$/ = undef; #slurp
	print $fdOut (<$fdIn>);
}
