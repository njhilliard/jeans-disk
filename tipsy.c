#include <stdio.h>
#include <errno.h>
#include <string.h>
#include "tipsy.h"

/* These are not exported */
static FILE* fd = NULL;
static float velocity_scale = 1.0f;
static float mass_scale = 1.0f;
static const char* last_system_error = 0;

int make_error() {
	last_system_error = strerror(EINVAL);
	return TIPSY_BAD_WRITE;
}

const char* tipsy_get_last_system_error() {
	return last_system_error;
}

const char* tipsy_strerror(tipsy_error err) {
	switch (err) {
	case TIPSY_ALREADY_OPEN:
		return "Tipsy file is already open";
	case TIPSY_BAD_ALLOC:
		return "Error opening Tipsy file";
	case TIPSY_READ_UNOPENED:
		return "Attempt to read from unopened file";
	case TIPSY_WRITE_UNOPENED:
		return "Attempt to write to unopened file";
	case TIPSY_BAD_WRITE:
		return "Error writing to Tipsy file";
	case TIPSY_BAD_READ:
		return "Error reading from Tipsy file";
	}
	return "";
}

void tipsy_set_velocity_scale(float vs) {
	velocity_scale = vs;
}

void tipsy_set_mass_scale(float ms) {
	mass_scale = ms;
}

int tipsy_open_file(const char *filename, const char *mode) {
	if (fd)
		return TIPSY_ALREADY_OPEN;

	fd = fopen(filename, mode);

	if (!fd) {
		last_system_error = strerror(errno);
		return TIPSY_BAD_ALLOC;
	}

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
		return TIPSY_WRITE_UNOPENED;

	tipsy_header h = { time, ngas + ndark + nstar, 3, ngas, ndark, nstar };
	if (fwrite(&h, sizeof(tipsy_header), 1, fd) != 1) {
		last_system_error = strerror(errno);
		return TIPSY_BAD_WRITE;
	}

	return 0;
}

int tipsy_write_star_particles(const float *mass, const float (*pos)[3],
		const float (*vel)[3], const float *metals, const float *tform,
		float softening, size_t size) {

	if (!fd)
		return TIPSY_WRITE_UNOPENED;

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
			last_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_dark_particles(const float *mass, const float (*pos)[3],
		const float (*vel)[3], float softening, size_t size) {

	if (!fd)
		return TIPSY_WRITE_UNOPENED;

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
			last_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_gas_particles(const float *mass, const float (*pos)[3],
		const float (*vel)[3], const float *rho, const float *temp,
		const float *hsmooth, const float *metals, size_t size) {

	if (!fd)
		return TIPSY_WRITE_UNOPENED;

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
			last_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_blackhole_particles(const float *mass, const float (*pos)[3],
		const float (*vel)[3], const float softening, size_t size) {

	if (!fd)
		return TIPSY_WRITE_UNOPENED;

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
		p.metals = 0.0;	// These are not stars in GADGET, so there is no metalicity
		p.tform = -1.0;		// Negative tForm signals black hole to GASOLINE
		p.phi = 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, fd) != 1) {
			last_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}
	return 0;
}
