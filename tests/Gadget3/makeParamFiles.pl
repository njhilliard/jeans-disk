use strict;
use warnings;
use File::Path qw(mkpath);
use Cwd qw(cwd);

my %config = (
	'nogas' => {
		'cooling' => 0,
		'starformation' => 0
	},
	'gas' => {
		'cooling' => 0,
		'starformation' => 0
	},
	'gas+sfr' => {
		'cooling' => 1,
		'starformation' => 1
	}
);

my $sfr_params = "
CritPhysDensity                    0
MaxSfrTimescale                    4.5
CritOverDensity                    57.7
TempSupernova                      3e+08
TempClouds                         1000
FactorSN                           0.1
FactorEVP                          3000
WindEfficiency                     0.005
WindEnergyFraction                 0.0025
WindFreeTravelDensFac              0.1
WindFreeTravelMaxTimeFactor        1
";

my $base_dir = cwd();

my $sim_time 	  = 0.500;	# 500 Myrs
my $max_step 	  = 0.001;	# 1   Myr
my $snap_interval = 0.050;	# 50  Myrs

for my $type (keys %config) {
	my $dir = "$base_dir/$type";
	mkpath($dir) if (! -d $dir);
	
	open my $fdOut, '>', "$dir/${type}.params" or die "Unable to create $dir/${type}.params: $!\n";
	print $fdOut <<EOF
InitCondFile		$dir/$type
SnapshotFileBase	$type
OutputDir			$dir
TimeMax				$sim_time
CoolingOn			$config{$type}{'cooling'}
StarformationOn		$config{$type}{'starformation'}
TimeBetSnapshot		$snap_interval
TimeOfFirstSnapshot	$snap_interval
MaxSizeTimestep		$max_step
EOF
;

	open my $fdIn, '<', "$base_dir/params.template" or die "Unable to open $base_dir/params.template: $!\n";
	$/ = undef; #slurp
	print $fdOut (<$fdIn>);
	
	print $fdOut $sfr_params if $type eq 'gas+sfr';
}
