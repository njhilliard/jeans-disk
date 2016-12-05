#include "tipsyio.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>

static const char *tipsy_system_error = NULL;
static FILE *tipsy_fd = NULL;
static tipsy_header hdr;

static void tipsy_reset_fd(long offset) {
	rewind(tipsy_fd);
	int i = fseek(tipsy_fd, offset, SEEK_SET);
	(void)i;
}

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

FILE *tipsy_get_fd() { return tipsy_fd; }

/*************************************************************************************************************/

int tipsy_read_header(tipsy_header *h) {
	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_reset_fd(0);
	if (fread(h, sizeof(tipsy_header), 1, tipsy_fd) != 1) {
		tipsy_system_error = strerror(errno);
		return TIPSY_BAD_READ;
	}

	memcpy(&hdr, h, sizeof(tipsy_header));

	return 0;
}

/**
 * 	  NOTE: These functions all assume that tipsy_read_header has already
 * 	  		been called. Failure to do so results in undefined behavior.
  */

int tipsy_read_star_particles(tipsy_star_data *d) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_star_particle p;
	const size_t size = d->size;
	const long offset = (int)sizeof(tipsy_header) +
						hdr.ngas * (int)sizeof(tipsy_gas_particle) +
					    hdr.ndark * (int)sizeof(tipsy_dark_particle);
	tipsy_reset_fd(offset);
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		d->mass[i]   = p.mass;
		d->pos[i][0] = p.pos[0];
		d->pos[i][1] = p.pos[1];
		d->pos[i][2] = p.pos[2];
		d->vel[i][0] = p.vel[0];
		d->vel[i][1] = p.vel[1];
		d->vel[i][2] = p.vel[2];
		d->metals[i] = p.metals;
		d->tform[i]  = p.tform;
		d->phi[i]    = p.phi;
	}

	return 0;
}

int tipsy_read_dark_particles(tipsy_dark_data *d) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_dark_particle p;
	const size_t size = d->size;
	tipsy_reset_fd((int)sizeof(tipsy_header) + hdr.ngas * (int)sizeof(tipsy_gas_particle));
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_dark_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		d->mass[i]   = p.mass;
		d->pos[i][0] = p.pos[0];
		d->pos[i][1] = p.pos[1];
		d->pos[i][2] = p.pos[2];
		d->vel[i][0] = p.vel[0];
		d->vel[i][1] = p.vel[1];
		d->vel[i][2] = p.vel[2];
		d->phi[i]    = p.phi;
	}

	return 0;
}

int tipsy_read_gas_particles(tipsy_gas_data *d) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_gas_particle p;
	const size_t size = d->size;
	tipsy_reset_fd(sizeof(tipsy_header));
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_gas_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_READ;
		}
		d->mass[i]   = p.mass;
		d->pos[i][0] = p.pos[0];
		d->pos[i][1] = p.pos[1];
		d->pos[i][2] = p.pos[2];
		d->vel[i][0] = p.vel[0];
		d->vel[i][1] = p.vel[1];
		d->vel[i][2] = p.vel[2];
		d->metals[i] = p.metals;
		d->phi[i]    = p.phi;
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

int tipsy_write_gas_particles(const float *mass,
			      const float (*pos)[3],
			      const float (*vel)[3],
			      const float *rho,
			      const float *temp,
			      const float *hsmooth,
			      const float *metals,
				  const float *phi,
			      const size_t size) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_gas_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass    = mass[i];
		p.pos[0]  = pos[i][0];
		p.pos[1]  = pos[i][1];
		p.pos[2]  = pos[i][2];
		p.vel[0]  = vel[i][0];
		p.vel[1]  = vel[i][1];
		p.vel[2]  = vel[i][2];
		p.rho     = rho[i];
		p.temp    = temp[i];
		p.hsmooth = hsmooth[i];
		p.metals  = (metals) ? metals[i] : 0.0f;
		p.phi     = (phi) ? phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_gas_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_dark_particles(const float *mass,
			       const float (*pos)[3],
			       const float (*vel)[3],
				   const float *phi,
			       const float  softening,
			       const size_t size) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_dark_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = mass[i];
		p.pos[0]    = pos[i][0];
		p.pos[1]    = pos[i][1];
		p.pos[2]    = pos[i][2];
		p.vel[0]    = vel[i][0];
		p.vel[1]    = vel[i][1];
		p.vel[2]    = vel[i][2];
		p.softening = softening;
		p.phi       = (phi) ? phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_dark_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_star_particles(const float *mass,
			       const float (*pos)[3],
			       const float (*vel)[3],
			       const float *metals,
			       const float *tform,
				   const float *phi,
			       const float	softening,
			       const size_t size,
				   const int	is_blackhole) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	// Negative tForm signals black hole to GASOLINE
	const float tform_default = (is_blackhole) ? -1.0 : 0.0;

	tipsy_star_particle p;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = mass[i];
		p.pos[0]    = pos[i][0];
		p.pos[1]    = pos[i][1];
		p.pos[2]    = pos[i][2];
		p.vel[0]    = vel[i][0];
		p.vel[1]    = vel[i][1];
		p.vel[2]    = vel[i][2];
		p.softening = softening;
		p.metals    = (metals) ? metals[i] : 0.0f;
		p.tform     = (tform) ? tform[i] : tform_default;
		p.phi       = (phi) ? phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

