#ifndef TIPSY_H
#define TIPSY_H

typedef struct {
	float mass;
	float pos[3];
	float vel[3];
	float rho;
	float temp;
	float hsmooth;
	float metals;
	float phi;
} tipsy_gas_particle;

typedef struct {
	float mass;
	float pos[3];
	float vel[3];
	float softening;
	float phi;
} tipsy_dark_particle;

typedef struct {
	float mass;
	float pos[3];
	float vel[3];
	float metals;
	float tform;
	float softening;
	float phi;
} tipsy_star_particle;

typedef struct {
	double time;
	int nbodies;
	int ndim;
	int ngas;
	int ndark;
	int nstar;
} tipsy_header;

void set_velocity_scale(float);
void set_mass_scale(float);
int tipsy_open_file(const char*, const char*);
void tipsy_close_file();
int tipsy_write_header(double, int, int, int);
int tipsy_write_star_particles(float*, float(*)[3], float(*)[3], float*, float*, float, size_t);
int tipsy_write_dark_particles(float*, float(*)[3], float(*)[3], float, size_t);
int tipsy_write_gas_particles(float*, float(*)[3], float(*)[3], float*, float*, float*, float*, size_t);
int tipsy_write_blackhole_particles(float*, float(*)[3], float(*)[3], float, size_t);

#endif
