#include <stdio.h>
#include <errno.h>

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

/* These are exported */
int tipsy_init(const char*, float, float);
int tipsy_open_file(const char*);
void tipsy_close_file();
int tipsy_write_header(double, int, int, int);
int tipsy_write_star_particles(float*, float**, float**, float*, float*, float,
		size_t);
int tipsy_write_dark_particles(float*, float**, float**, float, size_t);
int tipsy_write_gas_particles(float*, float**, float**, float*, float*, float*,
		float*, size_t);

/* These are not exported */
static FILE* fd = NULL;
static float velocity_scale = 1.0f;
static float mass_scale = 1.0f;

int tipsy_open_file(const char *filename) {
	if (fd)
		return -1;

	fd = fopen(filename, "wb");

	if (!fd)
		return -1;

	return 0;
}

void tipsy_close_file() {
	if (fd)
		fclose(fd);
}

int tipsy_init(const char* filename, float vscale, float mscale) {
	if (tipsy_open_file(filename)) {
		return -1;
	}

	velocity_scale = vscale;
	mass_scale = mscale;

	return 0;
}

int tipsy_write_header(double time, int ngas, int ndark, int nstar) {
	if (!fd)
		return -1;

	tipsy_header h = { time, ngas + ndark + nstar, 3, ngas, ndark, nstar };
	if (fwrite(&h, sizeof(tipsy_header), 1, fd) != 1) {
		return errno;
	}

	return 0;
}

int tipsy_write_star_particles(float *mass, float **pos, float **vel,
		float *metals, float *tform, float softening, size_t size) {

	if (!fd)
		return -1;

	tipsy_star_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass = mass[i] * mass_scale;
		p.pos[0] = pos[i][0];
		p.pos[1] = pos[i][1];
		p.pos[2] = pos[i][2];
		p.vel[0] = vel[i][0] * velocity_scale;
		p.vel[1] = vel[i][1] * velocity_scale;
		p.vel[2] = vel[i][2] * velocity_scale;
		p.softening = softening;
		p.metals = metals[i];
		p.tform = tform[i];
		p.phi = 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, fd) != 1) {
			return errno;
		}
	}

	return 0;

}

int tipsy_write_dark_particles(float *mass, float **pos, float **vel,
		float softening, size_t size) {

	if (!fd)
		return -1;

	tipsy_dark_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass = mass[i] * mass_scale;
		p.pos[0] = pos[i][0];
		p.pos[1] = pos[i][1];
		p.pos[2] = pos[i][2];
		p.vel[0] = vel[i][0] * velocity_scale;
		p.vel[1] = vel[i][1] * velocity_scale;
		p.vel[2] = vel[i][2] * velocity_scale;
		p.softening = softening;
		p.phi = 0.0f;

		if (fwrite(&p, sizeof(tipsy_dark_particle), 1, fd) != 1) {
			return errno;
		}
	}

	return 0;
}

int tipsy_write_gas_particles(float *mass, float **pos, float **vel, float *rho,
		float *temp, float *hsmooth, float *metals, size_t size) {

	if (!fd)
		return -1;

	tipsy_gas_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass = mass[i] * mass_scale;
		p.pos[0] = pos[i][0];
		p.pos[1] = pos[i][1];
		p.pos[2] = pos[i][2];
		p.vel[0] = vel[i][0] * velocity_scale;
		p.vel[1] = vel[i][1] * velocity_scale;
		p.vel[2] = vel[i][2] * velocity_scale;
		p.rho = rho[i];
		p.temp = temp[i];
		p.hsmooth = hsmooth[i];
		p.metals = metals[i];
		p.phi = 0.0f;

		if (fwrite(&p, sizeof(tipsy_gas_particle), 1, fd) != 1) {
			return errno;
		}
	}

	return 0;
}
