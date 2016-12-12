use strict;
use warnings;
use Cwd qw(cwd);

my $num_tasks = 128;
my $tasks_per_node = 16;
my $num_nodes = $num_tasks / $tasks_per_node;

my $base_dir = cwd();

sub write_header($$$) {
	my ($fdOut, $name, $output_dir) = @_;

	print $fdOut qq(#!/bin/sh

#SBATCH --job-name=$name
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

for my $type ('nogas', 'gas') {
	open my $fdOut, '>', "Gadget3.$type.sbatch" or die "Unable to create Gadget3.$type.sbatch: $!\n";
	write_header($fdOut, 'gad'.$type, "$base_dir/Gadget3/$type");
	print $fdOut "mpiexec -np $num_tasks $base_dir/Gadget3/$type/Gadget3 $base_dir/Gadget3/$type/${type}.params\n\n";
	close $fdOut;
	
	open $fdOut, '>', "ChaNGa.$type.sbatch" or die "Unable to create $base_dir/ChaNGa.$type.sbatch: $!\n";
	write_header($fdOut, 'cha'.$type, "$base_dir/ChaNGa/$type");
	print $fdOut "$base_dir/ChaNGa/$type/charmrun ++mpiexec ++p $num_tasks ++ppn 1 $base_dir/ChaNGa/$type/ChaNGa -v 1 $base_dir/ChaNGa/$type/$type.tipsy.ChaNGa.params\n\n";
}
