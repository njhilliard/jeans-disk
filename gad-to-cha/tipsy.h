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

// Convention: Positive are system errors, negative are Tipsy errors
typedef enum {
	TIPSY_BAD_ALLOC 		=  1, /* Error opening file */
	TIPSY_BAD_WRITE 		=  2, /* Bad write to file */
	TIPSY_BAD_READ 			=  3, /* Bad read from file */
	TIPSY_ALREADY_OPEN 		= -1, /* Tried to open an existing file */
	TIPSY_READ_UNOPENED 	= -2, /* Read from unopened file */
	TIPSY_WRITE_UNOPENED 	= -3, /* Write to unopened file */
} tipsy_error;

void set_velocity_scale(float);
void set_mass_scale(float);
int tipsy_open_file(const char*, const char*);
void tipsy_close_file();
int tipsy_write_header(double, int, int, int);
int tipsy_write_star_particles(const float*, const float(*)[3], const float(*)[3], const float*, const float*, float, size_t);
int tipsy_write_dark_particles(const float*, const float(*)[3], const float(*)[3], float, size_t);
int tipsy_write_gas_particles(const float*, const float(*)[3], const float(*)[3], const float*, const float*, const float*, const float*, size_t);
int tipsy_write_blackhole_particles(const float*, const float(*)[3], const float(*)[3], float, size_t);

const char* tipsy_get_last_system_error();
const char* tipsy_strerror(tipsy_error);

#endif
