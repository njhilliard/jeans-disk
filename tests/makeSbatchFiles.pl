use strict;
use warnings;
use Cwd qw(cwd);

my $num_tasks = 128;
my $tasks_per_node = 16;
my $num_nodes = $num_tasks / $tasks_per_node;
my $num_threads = $tasks_per_node - 2;

my $base_dir = cwd();

sub write_header($$$) {
	my ($fdOut, $type, $output_dir) = @_;

	print $fdOut qq(#!/bin/sh

#SBATCH --job-name=$type
#SBATCH --partition=ladon
#SBATCH --time=0-47:45:00    # run time in days-hh:mm:ss
#SBATCH --nodes=$num_nodes
#SBATCH --ntasks=$num_tasks
#SBATCH --ntasks-per-node=$tasks_per_node
#SBATCH --error=${output_dir}/stderr
#SBATCH --output=${output_dir}/stdout
#SBATCH --mail-type=fail
#SBATCH --mail-user=thaines\@astro.wisc.edu

);
}

for my $type ('nogas', 'gas', 'gas+sfr') {
	open my $fdOut, '>', "$type.Gadget3.sbatch" or die "Unable to create $type.Gadget3.sbatch: $!\n";
	write_header($fdOut, $type, "$base_dir/Gadget3/$type");
	print $fdOut "mpiexec -np $num_tasks $base_dir/Gadget3/$type/Gadget3 $base_dir/Gadget3/$type/${type}.params\n\n";
	close $fdOut;
	
	open $fdOut, '>', "$type.ChaNGa.sbatch" or die "Unable to create $base_dir/$type.ChaNGa.sbatch: $!\n";
	write_header($fdOut, $type, "$base_dir/ChaNGa/$type");
	print $fdOut "$base_dir/ChaNGa/$type/charmrun ++ppn $num_threads +p $num_nodes $base_dir/ChaNGa/$type/ChaNGa -v 1 $base_dir/ChaNGa/$type/$type.tipsy.ChaNGa.params\n\n";
}
