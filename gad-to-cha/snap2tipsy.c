#include <assert.h>
#include <endian.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXDIM 3

struct gas_particle {
	float mass;
	float pos[MAXDIM];
	float vel[MAXDIM];
	float rho;
	float temp;
	float hsmooth;
	float metals;
	float phi;
};

struct dark_particle {
	float mass;
	float pos[MAXDIM];
	float vel[MAXDIM];
	float eps;
	float phi;
};

struct star_particle {
	float mass;
	float pos[MAXDIM];
	float vel[MAXDIM];
	float metals;
	float tform;
	float eps;
	float phi;
};

struct dump {
	double time;
	int nbodies;
	int ndim;
	int nsph;
	int ndark;
	int nstar;
};

struct dump header;

#ifdef GADGET_DOUBLE
typedef double GFloat;
#else
typedef float GFloat;
#endif

double G, Hubble; /* H_0 in 100 km/s/Mpc */

typedef struct io_header_1 {
	int npart[6];
	double mass[6];
	double time;
	double redshift;
	int flag_sfr;
	int flag_feedback;
	int npartTotal[6];
	int flag_cooling;
	int num_files;
	double BoxSize;
	double Omega0;
	double OmegaLambda;
	double HubbleParam;
	/* Assuming TJ format */
	int flag_multiphase;
	int flag_stellarage;
	int flag_sfrhistogram;
	int flag_stargens;
	int flag_snapaspot;
	int flag_metals;
	int flag_energydetail;
	int flag_parentID;
	int flag_starorig;
	char fill[256 - 6 * 4 - 6 * 8 - 2 * 8 - 2 * 4 - 6 * 4 - 2 * 4 - 4 * 8 - 9 * 4]; /* fills to 256 Bytes */
} header1;

double softenings[6]; /* Gravitational softenings for each particle type */

#define TYPE_GAS 0
#define TYPE_HALO 1
#define TYPE_DISK 2
#define TYPE_BULGE 3
#define TYPE_STAR 4
#define TYPE_BNDRY 5

int NumPart, NumPartFiltered;

struct particle_data {
	GFloat Pos[3];
	GFloat Vel[3];
	GFloat Mass, Rho, Temp, Ne, Hsml; /* temp */
	GFloat tForm;
	GFloat Metals;
	int Flag;
} * P;

int *Id;

double Time, Redshift;

struct gas_particle gasp;
struct dark_particle darkp;
struct star_particle starp;

void free_memory(void);
void allocate_memory(void);
void load_snapshot(char *fname, int files, int type, float);
void update_tipsy_header(char *output_fname);
void filter_darkmatter();
void filter_star();
void filter_gas();
int output_tipsy_gas(char *output_fname);
int output_tipsy_star(char *output_fname, int bBH);
int output_tipsy_dark(char *output_fname, int type);
void set_unit();

/* Here we load a snapshot file. It can be distributed
 * onto several files (for files>1).
 * The particles are brought back into the order
 * implied by their ID's.
 * A unit conversion routine is called to do unit
 * conversion, and to evaluate the gas temperature.
 */
int main(int argc, char **argv) {
	char output_fname[200], input_fname[200], basename[200];
	int type, files;
	int bBHBndry; /* Boundary (type = 5) particles are really Black Holes */

	if (argc < 12) {
		fprintf(stderr, "usage: snap2tipsy h eps_gas eps_dark eps_disk eps_bulge eps_star eps_bndry(BH) ");
		fprintf(stderr, "bBH massScale <snapshotfile> <tipsyfile> [N_files]\n");
		fprintf(stderr, "	where h is H_0 in 100 km/s/Mpc and softenings are in kpc/h\n");
		fprintf(stderr, "	bBH = 1 implies type = 5 particles are black holes.\n");
		exit(-1);
	}

	Hubble = atof(argv[1]);
	for (type = 0; type < 6; type++) {
		softenings[type] = atof(argv[2 + type]);
	}

	bBHBndry = atoi(argv[8]);
	strcpy(basename, argv[9]);
	strcpy(output_fname, argv[10]);
	float mass_scale = atof(argv[11]);

	if (argc == 12) {
		files = atoi(argv[11]); /* # of files per snapshot */
	} else
		files = 1;

	sprintf(input_fname, "%s", basename);

	printf("loading gas particles...\n");

	load_snapshot(input_fname, files, type = 0, mass_scale);

	set_unit();

	filter_gas();
	output_tipsy_gas(output_fname);
	free_memory();

	printf("loading dark matter particles...\n");
	load_snapshot(input_fname, files, type = 1);
	filter_darkmatter();
	output_tipsy_dark(output_fname, type);
	free_memory();

	/* Handle funny component particles from Gadget.  Here we assume
	 that these types are collisionless only.  */
	if (header1.redshift != 0.0) {
		printf("loading disk particles... ");
		load_snapshot(input_fname, files, type = 2);
		filter_darkmatter();
		printf("and changing them to dark...\n");
		output_tipsy_dark(output_fname, type);
		free_memory();

		printf("loading bulge particles... ");
		load_snapshot(input_fname, files, type = 3);
		filter_darkmatter();
		printf("and changing them to dark...\n");
		output_tipsy_dark(output_fname, type);
		free_memory();
	} else {
		printf("loading disk particles... ");
		load_snapshot(input_fname, files, type = 2);
		filter_star();
		output_tipsy_star(output_fname, type);
		free_memory();

		printf("loading bulge particles... ");
		load_snapshot(input_fname, files, type = 3);
		filter_star();
		output_tipsy_star(output_fname, type);
		free_memory();
	}

	if (!bBHBndry) {
		printf("loading boundary particles... ");
		load_snapshot(input_fname, files, type = 5);
		filter_darkmatter();
		printf("and changing them to dark...\n");
		output_tipsy_dark(output_fname, 1);
		free_memory();
	}

	printf("loading star particles... ");
	load_snapshot(input_fname, files, type = 4);
	filter_star();
	output_tipsy_star(output_fname, 0);
	free_memory();

	if (bBHBndry) {
		printf("loading black hole particles... ");
		load_snapshot(input_fname, files, type = 5);
		filter_darkmatter();
		printf("and changing them to star...\n");
		output_tipsy_star(output_fname, 1);
		free_memory();
	}

	update_tipsy_header(output_fname);

	exit(0);
}

struct units {
	double Length_in_cm;
	double Mass_in_g;
	double Velocity_in_cm_per_s;
	double Time_in_s;
	double Time_in_Megayears;
	double Density_in_cgs;
	double Pressure_in_cgs;
	double CoolingRate_in_cgs;
	double Energy_in_cgs;
	double Natural_vel_in_cgs; /* sqrt(M/r) with G=1 */
} Unit;

void set_unit() {
/*
 * Assume length in kpc and mass in 1e10 Solarmasses
 */
#define GRAVITY 6.672e-8
#define SOLAR_MASS 1.989e33
#define SOLAR_LUM 3.826e33
#define RAD_CONST 7.565e-15
#define AVOGADRO 6.0222e23
#define BOLTZMANN 1.3806e-16
#define GAS_CONST 8.31425e7
#define C 2.9979e10
#define PLANCK 6.6262e-27
#define CM_PER_KPC 3.085678e21
#define PROTONMASS 1.6726e-24
#define HUBBLE 3.2407789e-18 /* in h/sec */
#define SEC_PER_MEGAYEAR 3.155e13
#define SEC_PER_YEAR 3.155e7
#define GAMMA (5.0 / 3)
#define GAMMA_MINUS1 (GAMMA - 1)

#define H_MASSFRAC 0.76

	if (Hubble == 0.0)
		Hubble = 1.0;

	Unit.Length_in_cm = CM_PER_KPC / Hubble;
	Unit.Mass_in_g = SOLAR_MASS * 1.0e10 / Hubble;
	Unit.Velocity_in_cm_per_s = 1e5;
	Unit.Time_in_s = Unit.Length_in_cm / Unit.Velocity_in_cm_per_s;
	Unit.Time_in_Megayears = Unit.Time_in_s / SEC_PER_MEGAYEAR;
	Unit.Density_in_cgs = Unit.Mass_in_g / pow(Unit.Length_in_cm, 3);
	Unit.Pressure_in_cgs = Unit.Mass_in_g / Unit.Length_in_cm / pow(Unit.Time_in_s, 2);
	Unit.CoolingRate_in_cgs = Unit.Pressure_in_cgs / Unit.Time_in_s;
	Unit.Energy_in_cgs = Unit.Mass_in_g * pow(Unit.Length_in_cm, 2) / pow(Unit.Time_in_s, 2);
	Unit.Natural_vel_in_cgs = sqrt(GRAVITY * Unit.Mass_in_g / Unit.Length_in_cm);

	fprintf(stdout, "dMsolUnit is %g; dKpcUnit is %g;\n", 1e10 / Hubble, 1.0 / Hubble);
	fprintf(stdout, "velocity is in units of %g km/s; time is in units of %g Gyr\n", Unit.Natural_vel_in_cgs / 1e5,
			Unit.Length_in_cm / Unit.Natural_vel_in_cgs / (1e9 * SEC_PER_YEAR));
	fprintf(stdout, "time is in units of %g Gyr\n", Unit.Time_in_s / ((1e9 * SEC_PER_YEAR)));
	fprintf(stdout, "G is %g in these units\n",
			GRAVITY / pow(Unit.Length_in_cm, 3) * Unit.Mass_in_g * pow(Unit.Time_in_s, 2));
}

void filter_gas() {
	int i;

	double Xh = H_MASSFRAC; /* mass fraction of hydrogen */
	double MeanWeight, rhomean;

	/* first, let's compute the temperature */

	for (i = 1; i <= NumPart; i++) {
		MeanWeight = 4.0 / (3 * Xh + 1 + 4 * Xh * P[i].Ne) * PROTONMASS;

		P[i].Temp *= MeanWeight / BOLTZMANN * GAMMA_MINUS1 * Unit.Energy_in_cgs / Unit.Mass_in_g;

		/* temp now in kelvin */
	}

	if (header1.Omega0 != 0.0) {
		rhomean = header1.Omega0 * 3 * Hubble * Hubble / (8 * M_PI * G);
	} else {
		rhomean = 1.0;
	}

	NumPartFiltered = 0;

	for (i = 1; i <= NumPart; i++) {

		/* these are just silly values for the moment, so that
		 everything will be selected */

		if (P[i].Temp > -100000 && P[i].Rho / rhomean > -1000.) {
			P[i].Flag = 1; /* take it */
			NumPartFiltered++;
		} else
			P[i].Flag = 0; /* discard */
	}
}

void filter_darkmatter() {
	int i;

	NumPartFiltered = 0;
	for (i = 1; i <= NumPart; i++) {
		P[i].Flag = 1; /* keep- set this to 0 to discard */
		NumPartFiltered++;
	}
}

void filter_star() {
	int i;

	NumPartFiltered = 0;
	for (i = 1; i <= NumPart; i++) {
		P[i].Flag = 1; /* keep- set this to 0 to discard */
		NumPartFiltered++;
	}
}

int output_tipsy_gas(char *output_fname) {
	int i;
	FILE *outfile;
	/* Gadget units have an extra sqrt(a) in the internal velocities. */
	double vscale = sqrt(1.0 + header1.redshift);
	/*
	 *Unit.Velocity_in_cm_per_s/Unit.Natural_vel_in_cgs;
	 */

	if (!(outfile = fopen(output_fname, "w"))) {
		printf("can't open file `%s'\n", output_fname);
		exit(0);
	}

	printf("velocity scaling: %g\n", vscale);

	/* Load tipsy header */
	header.time = header1.time;
	header.nbodies = NumPartFiltered;
	header.ndim = 3;
	header.nsph = NumPartFiltered;
	header.ndark = 0;
	header.nstar = 0; /*  header1.npartTotal[4]; */

	fwrite(&header, sizeof(header), 1, outfile);

	for (i = 1; i <= NumPart; i++) {
		if (P[i].Flag) {
			gasp.mass = P[i].Mass;
			/*      printf("gas mass %f ...\n",P[i].Mass); */
			gasp.pos[0] = P[i].Pos[0];
			gasp.pos[1] = P[i].Pos[1];
			gasp.pos[2] = P[i].Pos[2];
			gasp.vel[0] = P[i].Vel[0] * vscale;
			gasp.vel[1] = P[i].Vel[1] * vscale;
			gasp.vel[2] = P[i].Vel[2] * vscale;
			gasp.temp = P[i].Temp;
			gasp.hsmooth = softenings[TYPE_GAS];
			gasp.rho = P[i].Rho;
			gasp.metals = P[i].Metals;
			gasp.phi = 0.0;

			fwrite(&gasp, sizeof(struct gas_particle), 1, outfile);
		}
	}

	fclose(outfile);

	return 0;
}

int output_tipsy_star(char *output_fname, int bBH) {
	int i;
	FILE *outfile;
	/* Gadget units have an extra sqrt(a) in the internal velocities. */
	double vscale = sqrt(1.0 + header1.redshift);
	/*
	 *Unit.Velocity_in_cm_per_s/Unit.Natural_vel_in_cgs;
	 */

	if (!(outfile = fopen(output_fname, "a"))) {
		printf("can't open file `%s'\n", output_fname);
		exit(0);
	}

	for (i = 1; i <= NumPart; i++) {
		if (P[i].Flag) {
			starp.mass = P[i].Mass;
			starp.pos[0] = P[i].Pos[0];
			starp.pos[1] = P[i].Pos[1];
			starp.pos[2] = P[i].Pos[2];
			starp.vel[0] = P[i].Vel[0] * vscale;
			starp.vel[1] = P[i].Vel[1] * vscale;
			starp.vel[2] = P[i].Vel[2] * vscale;
			starp.metals = P[i].Metals;
			if (bBH) {
				/* Negative tForm signals black hole to GASOLINE */
				starp.tform = -1;
				starp.eps = softenings[TYPE_BNDRY];
			} else {
				starp.tform = P[i].tForm;
				starp.eps = softenings[TYPE_STAR];
			}
			starp.phi = 0.0;

			fwrite(&starp, sizeof(struct star_particle), 1, outfile);
		}
	}

	fclose(outfile);

	header.nbodies += NumPartFiltered;
	header.nstar += NumPartFiltered;

	printf("done.\n");

	return 0;
}

void update_tipsy_header(char *output_fname) {
	FILE *outfile;

	printf("updating tipsy header...\n");

	if (!(outfile = fopen(output_fname, "r+"))) {
		printf("can't open file `%s'\n", output_fname);
		exit(0);
	}

	printf("header.nsph= %d...\n", header.nsph);
	printf("header.ndark= %d...\n", header.ndark);
	printf("header.nstar= %d...\n", header.nstar);

	fwrite(&header, sizeof(header), 1, outfile);
	fclose(outfile);
}

int output_tipsy_dark(char *output_fname, int type) {
	int i;
	FILE *outfile;
	/* Gadget units have an extra sqrt(a) in the internal velocities. */
	double vscale = sqrt(1.0 + header1.redshift);
	/*
	 * Unit.Velocity_in_cm_per_s/Unit.Natural_vel_in_cgs;
	 */

	if (!(outfile = fopen(output_fname, "a"))) {
		printf("can't open file `%s'\n", output_fname);
		exit(0);
	}

	for (i = 1; i <= NumPart; i++) {
		if (P[i].Flag) {
			darkp.mass = P[i].Mass;
			darkp.pos[0] = P[i].Pos[0];
			darkp.pos[1] = P[i].Pos[1];
			darkp.pos[2] = P[i].Pos[2];
			darkp.vel[0] = P[i].Vel[0] * vscale;
			darkp.vel[1] = P[i].Vel[1] * vscale;
			darkp.vel[2] = P[i].Vel[2] * vscale;
			darkp.eps = softenings[type];
			darkp.phi = 0.;

			fwrite(&darkp, sizeof(struct dark_particle), 1, outfile);
		}
	}

	fclose(outfile);

	header.nbodies += NumPartFiltered;
	header.ndark += NumPartFiltered;

	printf("done.\n");

	return 0;
}

int SKIP(FILE *fd, int swap, int count) {
	int dummy;
	fread(&dummy, sizeof(dummy), 1, fd);
	if (swap)
		swapEndian(&dummy, sizeof(dummy), 1);
	fprintf(stderr, "At byte %ld: record size %d\n", ftell(fd), dummy);
	if (feof(fd))
		return 1;
	if (count == 2 * dummy || dummy == 2 * count) {
		fprintf(stderr, "Possible double vs float problem\n");
		fprintf(stderr, "Expected %d; got %d\n", count, dummy);
	}
	assert(dummy == count);
	return 0;
}

/* this routine loads particle data from Gadget's default
 * binary file format. (A snapshot may be distributed
 * into multiple files.
 */
void load_snapshot(char *fname, int files, int type, float mass_scale) {
	FILE *fd;
	char buf[200];
	int i, k, dummy, ntot_withmasses;
	int n, pc, pc_new, pc_sph;
	int pc_star;
	int nread;
	int swap = 0;
	double fMinMass = 1e38;
	double fMaxMass = 0.0;

	for (i = 0, pc = 1; i < files; i++, pc = pc_new) {
		int nTotPart = 0; /* Total particles in this file */
		if (files > 1)
			sprintf(buf, "%s.%d", fname, i);
		else
			sprintf(buf, "%s", fname);

		if (!(fd = fopen(buf, "r"))) {
			fprintf(stderr, "can't open file `%s`\n", buf);
			exit(0);
		}

		fread(&dummy, sizeof(dummy), 1, fd);
		if (dummy != sizeof(header1)) {
			swap = 1;
			fprintf(stderr, "Trying endian swap\n");
			swapEndian(&dummy, sizeof(dummy), 1);
			assert(dummy == sizeof(header1));
		}

		nread = fread(&header1, sizeof(header1), 1, fd);
		if (nread != 1) {
			fprintf(stderr, "Bad header read of %s\n", buf);
			exit(-1);
		}
		if (swap) {
			swapEndian(&header1, 4, 6);			  // 6 integers
			swapEndian(&header1.mass, 8, 8);	  // 8 doubles
			swapEndian(&header1.flag_sfr, 4, 10); // 10 more integers
			swapEndian(&header1.BoxSize, 8, 4);   // 4 more doubles
			swapEndian(&header1.flag_sfr, 4, 9);  // 9 more integers
		}

		fprintf(stderr, "time: %g\n", header1.time);
		fprintf(stderr, "redshift: %g\n", header1.redshift);
		fprintf(stderr, "BoxSize: %g\n", header1.BoxSize);
		fprintf(stderr, "Hubble parameter: %g\n", header1.HubbleParam);
		fprintf(stderr, "Omega0: %g\n", header1.Omega0);
		fprintf(stderr, "Lambda parameter: %g\n", header1.OmegaLambda);
		fread(&dummy, sizeof(dummy), 1, fd);

		if (files == 1) {
			NumPart = header1.npart[type];
		} else {
			NumPart = header1.npartTotal[type];
		}

		for (k = 0, ntot_withmasses = 0; k < 6; k++) {
			if (header1.mass[k] == 0)
				ntot_withmasses += header1.npart[k];
			nTotPart += header1.npart[k];
		}

		if (i == 0)
			allocate_memory();

		/*
		 * Positions
		 */
		SKIP(fd, swap, sizeof(GFloat) * 3 * nTotPart);
		for (k = 0, pc_new = pc; k < 6; k++) {
			if (k == type) {
				for (n = 0; n < header1.npart[k]; n++) {
					nread = fread(&P[pc_new].Pos[0], sizeof(GFloat), 3, fd);
					assert(nread == 3);
					if (swap)
						swapEndian(&P[pc_new].Pos[0], sizeof(GFloat), 3);
					pc_new++;
				}
			} else
				fseek(fd, sizeof(GFloat) * 3 * header1.npart[k], SEEK_CUR);
		}
		SKIP(fd, swap, sizeof(GFloat) * 3 * nTotPart);

		/*
		 * Velocities
		 */
		SKIP(fd, swap, sizeof(GFloat) * 3 * nTotPart);
		for (k = 0, pc_new = pc; k < 6; k++) {
			if (k == type) {
				for (n = 0; n < header1.npart[k]; n++) {
					nread = fread(&P[pc_new].Vel[0], sizeof(GFloat), 3, fd);
					assert(nread == 3);
					if (swap)
						swapEndian(&P[pc_new].Vel[0], sizeof(GFloat), 3);
					pc_new++;
				}
			} else
				fseek(fd, sizeof(GFloat) * 3 * header1.npart[k], SEEK_CUR);
		}
		SKIP(fd, swap, sizeof(GFloat) * 3 * nTotPart);

		/*
		 * IDs
		 */
		SKIP(fd, swap, sizeof(int) * 1 * nTotPart);
		for (k = 0, pc_new = pc; k < 6; k++) {
			if (k == type) {
				for (n = 0; n < header1.npart[k]; n++) {
					nread = fread(&Id[pc_new], sizeof(int), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&Id[pc_new], sizeof(int), 1);
					pc_new++;
				}
			} else
				fseek(fd, sizeof(int) * header1.npart[k], SEEK_CUR);
		}
		SKIP(fd, swap, sizeof(int) * 1 * nTotPart);

		/*----------------------------------------------------------*/

		/*
		 * Masses
		 */
		if (ntot_withmasses > 0)
			SKIP(fd, swap, sizeof(GFloat) * 1 * ntot_withmasses);

		for (k = 0, pc_new = pc; k < 6; k++) {
			if (k == type) {

				for (n = 0; n < header1.npart[k]; n++) {
					if (header1.mass[k] == 0) {
						nread = fread(&P[pc_new].Mass, sizeof(GFloat), 1, fd);
						assert(nread == 1);
						if (swap)
							swapEndian(&P[pc_new].Mass, sizeof(GFloat), 1);
					} else
						P[pc_new].Mass = header1.mass[k];
					if (P[pc_new].Mass > fMaxMass)
						fMaxMass = P[pc_new].Mass;
					if (P[pc_new].Mass < fMinMass)
						fMinMass = P[pc_new].Mass;
					P[pc_new].Mass *= mass_scale;
					pc_new++;
				}
			} else if (header1.mass[k] == 0) {
				for (n = 0; n < header1.npart[k]; n++) {
					fseek(fd, sizeof(GFloat), SEEK_CUR);
				}
			}
		}

		fprintf(stderr, "Mass range: %g to %g\n", fMinMass, fMaxMass);

		if (ntot_withmasses > 0)
			SKIP(fd, swap, sizeof(GFloat) * 1 * ntot_withmasses);

		/*----------------------------------------------------------*/
		/* Gas variables */

		/*
		 * Internal Energy (converted to Temperatures later)
		 */
		if (header1.npart[0] > 0 && type == 0) {
			int bEof;
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
				nread = fread(&P[pc_sph].Temp, sizeof(GFloat), 1, fd);
				if (nread != 1) {
					if (pc_sph == pc) {
						fprintf(stderr, "WARNING: No SPH temperatures\n");
						return;
					} else {
						fprintf(stderr, "Short read of temperatures\n");
						exit(-1);
					}
				}
				if (swap)
					swapEndian(&P[pc_sph].Temp, sizeof(GFloat), 1);
				pc_sph++;
			}
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);

			/*
			 * Densities
			 */
			bEof = SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			if (bEof) {
				fprintf(stderr, "No densities: end of file\n");
				fclose(fd);
				continue;
			}

			for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
				nread = fread(&P[pc_sph].Rho, sizeof(GFloat), 1, fd);
				if (nread != 1) {
					if (pc_sph == pc || n == 1) {
						fprintf(stderr, "WARNING: No SPH densities\n");
						n = 0;
						while (n < header1.npart[0]) {
							P[pc_sph].Rho = 0.0; /* fill in with zeros */
							n++;
							pc_sph++;
						}
						return;
					} else {
						fprintf(stderr, "Short read of densities at n = %d\n", n);
						exit(-1);
					}
				}
				if (swap)
					swapEndian(&P[pc_sph].Rho, sizeof(GFloat), 1);
				pc_sph++;
			}
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);

			/*
			 * Electron Density
			 */
			if (header1.flag_cooling) {
				SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					nread = fread(&P[pc_sph].Ne, sizeof(GFloat), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&P[pc_sph].Ne, sizeof(GFloat), 1);
					pc_sph++;
				}
				SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			} else
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					P[pc_sph].Ne = 1.0;
					pc_sph++;
				}

			/* now a dummy read of the neutral hydrogen into the hsm array */

			if (header1.flag_cooling) {
				SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					nread = fread(&P[pc_sph].Hsml, sizeof(GFloat), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&P[pc_sph].Hsml, sizeof(GFloat), 1);
					pc_sph++;
				}
				SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			} else
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					P[pc_sph].Hsml = 1.0;
					pc_sph++;
				}

			/* now really read hsm into the hsm array */

			if (header1.flag_cooling) {
				SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					nread = fread(&P[pc_sph].Hsml, sizeof(GFloat), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&P[pc_sph].Hsml, sizeof(GFloat), 1);
					pc_sph++;
				}
				SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			} else
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					P[pc_sph].Hsml = 1.0;
					pc_sph++;
				}

		} else {
			fseek(fd, 5 * (header1.npart[0] * sizeof(GFloat) + 2 * sizeof(int)), SEEK_CUR);
		}

		/*
		 * Skip star formation rate
		 */
		if (header1.flag_sfr == 1) {
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			fseek(fd, header1.npart[0] * sizeof(GFloat), SEEK_CUR);
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
		}
		if (header1.flag_stellarage) {
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[4]);
			if (type == 4) {
				for (n = 0, pc_star = pc; n < header1.npart[4]; n++) {
					nread = fread(&P[pc_star].tForm, sizeof(GFloat), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&P[pc_star].tForm, sizeof(GFloat), 1);
					pc_star++;
				}
			} else {
				fseek(fd, header1.npart[4] * sizeof(GFloat), SEEK_CUR);
			}
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[4]);
		}

		if (header1.flag_feedback) {
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			fseek(fd, header1.npart[0] * sizeof(GFloat), SEEK_CUR);
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
		}
		if (header1.flag_snapaspot == 1) {
			SKIP(fd, swap, sizeof(GFloat) * nTotPart);
			fseek(fd, nTotPart * sizeof(GFloat), SEEK_CUR);
			SKIP(fd, swap, sizeof(GFloat) * nTotPart);
		}
		if (header1.flag_metals) {
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			if (type == 0) {
				for (n = 0, pc_sph = pc; n < header1.npart[0]; n++) {
					nread = fread(&P[pc_sph].Metals, sizeof(GFloat), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&P[pc_sph].Metals, sizeof(GFloat), 1);
					pc_sph++;
				}
			} else {
				fseek(fd, header1.npart[0] * sizeof(GFloat), SEEK_CUR);
			}
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[0]);
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[4]);
			if (type == 4) {
				for (n = 0, pc_star = pc; n < header1.npart[4]; n++) {
					nread = fread(&P[pc_star].Metals, sizeof(GFloat), 1, fd);
					assert(nread == 1);
					if (swap)
						swapEndian(&P[pc_star].Metals, sizeof(GFloat), 1);
					pc_star++;
				}
			} else {
				fseek(fd, header1.npart[4] * sizeof(GFloat), SEEK_CUR);
			}
			SKIP(fd, swap, sizeof(GFloat) * 1 * header1.npart[4]);
		}
		/*----------------------------------------------------------*/
		/* Extra variables */
		/* Unfortunately, we have no clue what could come here.
		 * There could be POT, ACCEL, DTENTR, TSTP
		 */

		fclose(fd);
	}

	Time = header1.time;
	Redshift = header1.time;
}

/* this routine allocates the memory for the
 * particle data.
 */
void allocate_memory(void) {
	/*  fprintf(stderr,"allocating memory...\n");*/

	fprintf(stderr, "NumPart=%d \n", NumPart);

	if (!(P = malloc(NumPart * sizeof(struct particle_data)))) {
		fprintf(stderr, "failed to allocate memory.\n");
		exit(0);
	}

	P--; /* start with offset 1 */

	if (!(Id = malloc(NumPart * sizeof(int)))) {
		fprintf(stderr, "failed to allocate memory.\n");
		exit(0);
	}

	Id--; /* start with offset 1 */
}

void free_memory(void) {
	Id++;
	P++;
	free(Id);
	free(P);
}
