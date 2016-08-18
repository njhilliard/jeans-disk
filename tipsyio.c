#include "tipsyio.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>

static const char *tipsy_system_error = NULL;
static FILE *      tipsy_fd	   = NULL;

const char *tipsy_get_last_system_error() { return tipsy_system_error; }

const char *tipsy_strerror(tipsy_error_t err) {
	switch (err) {
	case TIPSY_BAD_OPEN:
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

int tipsy_open_file(const char *filename, const char *mode) {
	if (tipsy_fd) return 0;

	tipsy_fd = fopen(filename, mode);

	if (!tipsy_fd) {
		tipsy_system_error = strerror(errno);
		return TIPSY_BAD_OPEN;
	}

	return 0;
}

void tipsy_close_file() {
	if (tipsy_fd) {
		fclose(tipsy_fd);
		tipsy_fd = NULL;
	}
}

FILE* tipsy_get_fd() {
	return tipsy_fd;
}

/*************************************************************************************************************/

int tipsy_read_header(double *time, int *ngas, int *ndark, int *nstar) {
	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_header h;
	if (fread(&h, sizeof(tipsy_header), 1, tipsy_fd) != 1) {
		tipsy_system_error = strerror(errno);
		return TIPSY_BAD_READ;
	}

	*time  = h.time;
	*ngas  = h.ngas;
	*ndark = h.ndark;
	*nstar = h.nstar;

	return 0;
}

int tipsy_read_star_particles(float *mass,
			      float (*pos)[3],
			      float (*vel)[3],
			      float *metals,
			      float *tform,
			      float *phi,
			      size_t size) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_star_particle p;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		mass[i]   = p.mass;
		pos[i][0] = p.pos[0];
		pos[i][1] = p.pos[1];
		pos[i][2] = p.pos[2];
		vel[i][0] = p.vel[0];
		vel[i][1] = p.vel[1];
		vel[i][2] = p.vel[2];
		metals[i] = p.metals;
		tform[i]  = p.tform;
		phi[i]    = p.phi;
	}

	return 0;
}

int tipsy_read_dark_particles(float *mass, float (*pos)[3], float (*vel)[3], float *phi, size_t size) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_dark_particle p;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_dark_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		mass[i]   = p.mass;
		pos[i][0] = p.pos[0];
		pos[i][1] = p.pos[1];
		pos[i][2] = p.pos[2];
		vel[i][0] = p.vel[0];
		vel[i][1] = p.vel[1];
		vel[i][2] = p.vel[2];
		phi[i]    = p.phi;
	}

	return 0;
}

int tipsy_read_gas_particles(float *mass,
			     float (*pos)[3],
			     float (*vel)[3],
			     float *rho,
			     float *temp,
			     float *hsmooth,
			     float *metals,
			     float *phi,
			     size_t size) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_gas_particle p;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_gas_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		mass[i]   = p.mass;
		pos[i][0] = p.pos[0];
		pos[i][1] = p.pos[1];
		pos[i][2] = p.pos[2];
		vel[i][0] = p.vel[0];
		vel[i][1] = p.vel[1];
		vel[i][2] = p.vel[2];
		metals[i] = p.metals;
		phi[i]    = p.phi;
	}

	return 0;
}

int tipsy_read_blackhole_particles(float *mass, float (*pos)[3], float (*vel)[3], float *phi, size_t size) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_star_particle p;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		mass[i]   = p.mass;
		pos[i][0] = p.pos[0];
		pos[i][1] = p.pos[1];
		pos[i][2] = p.pos[2];
		vel[i][0] = p.vel[0];
		vel[i][1] = p.vel[1];
		vel[i][2] = p.vel[2];
		phi[i]    = p.phi;
	}
	return 0;
}

/*************************************************************************************************************/

int tipsy_write_header(double time, int ngas, int ndark, int nstar) {
	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_header h = {time, ngas + ndark + nstar, 3, ngas, ndark, nstar};
	if (fwrite(&h, sizeof(tipsy_header), 1, tipsy_fd) != 1) {
		tipsy_system_error = strerror(errno);
		return TIPSY_BAD_WRITE;
	}

	return 0;
}

int tipsy_write_star_particles(const float *mass,
			       const float (*pos)[3],
			       const float (*vel)[3],
			       const float *metals,
			       const float *tform,
			       float	softening,
			       float	mass_scale,
			       float	velocity_scale,
			       size_t       size) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_star_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = mass[i] * mass_scale;
		p.pos[0]    = pos[i][0];
		p.pos[1]    = pos[i][1];
		p.pos[2]    = pos[i][2];
		p.vel[0]    = vel[i][0] * velocity_scale;
		p.vel[1]    = vel[i][1] * velocity_scale;
		p.vel[2]    = vel[i][2] * velocity_scale;
		p.softening = softening;
		p.metals    = metals[i];
		p.tform     = tform[i];
		p.phi       = 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_dark_particles(const float *mass,
			       const float (*pos)[3],
			       const float (*vel)[3],
			       float  softening,
			       float  mass_scale,
			       float  velocity_scale,
			       size_t size) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_dark_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = mass[i] * mass_scale;
		p.pos[0]    = pos[i][0];
		p.pos[1]    = pos[i][1];
		p.pos[2]    = pos[i][2];
		p.vel[0]    = vel[i][0] * velocity_scale;
		p.vel[1]    = vel[i][1] * velocity_scale;
		p.vel[2]    = vel[i][2] * velocity_scale;
		p.softening = softening;
		p.phi       = 0.0f;

		if (fwrite(&p, sizeof(tipsy_dark_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_gas_particles(const float *mass,
			      const float (*pos)[3],
			      const float (*vel)[3],
			      const float *rho,
			      const float *temp,
			      const float *hsmooth,
			      const float *metals,
			      float	mass_scale,
			      float	velocity_scale,
			      size_t       size) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_gas_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass    = mass[i] * mass_scale;
		p.pos[0]  = pos[i][0];
		p.pos[1]  = pos[i][1];
		p.pos[2]  = pos[i][2];
		p.vel[0]  = vel[i][0] * velocity_scale;
		p.vel[1]  = vel[i][1] * velocity_scale;
		p.vel[2]  = vel[i][2] * velocity_scale;
		p.rho     = rho[i];
		p.temp    = temp[i];
		p.hsmooth = hsmooth[i];
		p.metals  = metals[i];
		p.phi     = 0.0f;

		if (fwrite(&p, sizeof(tipsy_gas_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_blackhole_particles(const float *mass,
				    const float (*pos)[3],
				    const float (*vel)[3],
				    const float softening,
				    float       mass_scale,
				    float       velocity_scale,
				    size_t      size) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_star_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = mass[i] * mass_scale;
		p.pos[0]    = pos[i][0];
		p.pos[1]    = pos[i][1];
		p.pos[2]    = pos[i][2];
		p.vel[0]    = vel[i][0] * velocity_scale;
		p.vel[1]    = vel[i][1] * velocity_scale;
		p.vel[2]    = vel[i][2] * velocity_scale;
		p.softening = softening;
		p.metals    = 0.0;  // These are not stars in GADGET, so there is no metalicity
		p.tform     = -1.0; // Negative tForm signals black hole to GASOLINE
		p.phi       = 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}
	return 0;
}
