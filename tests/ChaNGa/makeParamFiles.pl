use strict;
use warnings;
use File::Path qw(mkpath);
use Cwd qw(cwd);

my $base_dir = cwd();

for my $type ('nogas', 'gas') {
	my $dir = "$base_dir/$type";
	mkpath($dir) if (! -d $dir);
}
