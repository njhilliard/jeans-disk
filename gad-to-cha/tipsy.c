#include <stdio.h>
#include <errno.h>
#include "tipsy.h"

/* These are not exported */
static FILE* fd = NULL;
static float velocity_scale = 1.0f;
static float mass_scale = 1.0f;

void tipsy_set_velocity_scale(float vs) {
	velocity_scale = vs;
}

void tipsy_set_mass_scale(float ms) {
	mass_scale = ms;
}

int tipsy_open_file(const char *filename, const char *mode) {
	if (fd)
		return -1;

	fd = fopen(filename, mode);

	if (!fd)
		return -1;

	return 0;
}

void tipsy_close_file() {
	if (fd) {
		fclose(fd);
		fd = NULL;
	}
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

int tipsy_write_star_particles(float *mass, float (*pos)[3], float (*vel)[3],
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

int tipsy_write_dark_particles(float *mass, float (*pos)[3], float (*vel)[3],
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

int tipsy_write_gas_particles(float *mass, float (*pos)[3], float (*vel)[3], float *rho,
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

int tipsy_write_blackhole_particles(float *mass, float (*pos)[3], float (*vel)[3],
		float softening, size_t size) {

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
		p.metals = 0.0;		// These are not stars in GADGET, so there is no metalicity
		p.tform = -1.0;		// Negative tForm signals black hole to GASOLINE
		p.phi = 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, fd) != 1) {
			return errno;
		}
	}
	return 0;
}
