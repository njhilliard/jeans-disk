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

FILE *tipsy_get_fd() { return tipsy_fd; }

/*************************************************************************************************************/

int tipsy_read_header(tipsy_header *h) {
	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	if (fread(h, sizeof(tipsy_header), 1, tipsy_fd) != 1) {
		tipsy_system_error = strerror(errno);
		return TIPSY_BAD_READ;
	}

	return 0;
}

int tipsy_read_star_particles(tipsy_star_data *d) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_star_particle p;
	const size_t	size = d->size;
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
	const size_t	size = d->size;
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
	const size_t       size = d->size;
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

int tipsy_read_blackhole_particles(tipsy_blackhole_data *d) {

	if (!tipsy_fd) { return TIPSY_READ_UNOPENED; }

	tipsy_star_particle p;
	const size_t	size = d->size;
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
		d->phi[i]    = p.phi;
	}
	return 0;
}

/*************************************************************************************************************/

int tipsy_write_header(tipsy_header const *h) {
	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	if (fwrite(h, sizeof(tipsy_header), 1, tipsy_fd) != 1) {
		tipsy_system_error = strerror(errno);
		return TIPSY_BAD_WRITE;
	}

	return 0;
}

int tipsy_write_star_particles(tipsy_star_data const *d) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_star_particle p;
	const size_t	size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = d->mass[i];
		p.pos[0]    = d->pos[i][0];
		p.pos[1]    = d->pos[i][1];
		p.pos[2]    = d->pos[i][2];
		p.vel[0]    = d->vel[i][0];
		p.vel[1]    = d->vel[i][1];
		p.vel[2]    = d->vel[i][2];
		p.softening = d->soft;
		p.metals    = (d->metals) ? d->metals[i] : 0.0f;
		p.tform     = (d->tform) ? d->tform[i] : 0.0f;
		p.phi       = (d->phi) ? d->phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_dark_particles(tipsy_dark_data const *d) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_dark_particle p;
	const size_t	size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = d->mass[i];
		p.pos[0]    = d->pos[i][0];
		p.pos[1]    = d->pos[i][1];
		p.pos[2]    = d->pos[i][2];
		p.vel[0]    = d->vel[i][0];
		p.vel[1]    = d->vel[i][1];
		p.vel[2]    = d->vel[i][2];
		p.softening = d->soft;
		p.phi       = (d->phi) ? d->phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_dark_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_gas_particles(tipsy_gas_data const *d) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_gas_particle p;
	const size_t       size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass    = d->mass[i];
		p.pos[0]  = d->pos[i][0];
		p.pos[1]  = d->pos[i][1];
		p.pos[2]  = d->pos[i][2];
		p.vel[0]  = d->vel[i][0];
		p.vel[1]  = d->vel[i][1];
		p.vel[2]  = d->vel[i][2];
		p.rho     = d->rho[i];
		p.temp    = d->temp[i];
		p.hsmooth = d->hsmooth[i];
		p.metals  = (d->metals) ? d->metals[i] : 0.0f;
		p.phi     = (d->phi) ? d->phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_gas_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}

	return 0;
}

int tipsy_write_blackhole_particles(tipsy_blackhole_data const *d) {

	if (!tipsy_fd) { return TIPSY_WRITE_UNOPENED; }

	tipsy_star_particle p;
	const size_t	size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = d->mass[i];
		p.pos[0]    = d->pos[i][0];
		p.pos[1]    = d->pos[i][1];
		p.pos[2]    = d->pos[i][2];
		p.vel[0]    = d->vel[i][0];
		p.vel[1]    = d->vel[i][1];
		p.vel[2]    = d->vel[i][2];
		p.softening = d->soft;
		p.metals    = 0.0;
		p.tform     = -1.0; // Negative tForm signals black hole to GASOLINE
		p.phi       = (d->phi) ? d->phi[i] : 0.0f;

		if (fwrite(&p, sizeof(tipsy_star_particle), 1, tipsy_fd) != 1) {
			tipsy_system_error = strerror(errno);
			return TIPSY_BAD_WRITE;
		}
	}
	return 0;
}
