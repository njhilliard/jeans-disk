#pragma once

#include <stdio.h>
#include "tipsy.h"

// Convention: Positive are system errors, negative are Tipsy errors
typedef enum {
	TIPSY_BAD_OPEN  		=  1, /* Error opening file */
	TIPSY_BAD_WRITE 		=  2, /* Bad write to file */
	TIPSY_BAD_READ 			=  3, /* Bad read from file */
	TIPSY_READ_UNOPENED 	= -1, /* Read from unopened file */
	TIPSY_WRITE_UNOPENED 	= -2, /* Write to unopened file */
} tipsy_error_t;

int 		tipsy_open_file(const char*, const char*);
void 		tipsy_close_file();
FILE 	  * tipsy_get_fd();
const char* tipsy_get_last_system_error();
const char* tipsy_strerror(tipsy_error_t);

int tipsy_read_header(tipsy_header*);
int tipsy_read_star_particles(tipsy_star_data*);
int tipsy_read_dark_particles(tipsy_dark_data*);
int tipsy_read_gas_particles(tipsy_gas_data*);

int tipsy_write_header(double time, int ngas, int ndark, int nstar);

int tipsy_write_star_particles(const float *mass,
			       const float (*pos)[3],
			       const float (*vel)[3],
			       const float *metals,
			       const float *tform,
			       float	softening,
			       size_t   size);

int tipsy_write_dark_particles(const float *mass,
			       const float (*pos)[3],
			       const float (*vel)[3],
			       float  softening,
			       size_t size);

int tipsy_write_gas_particles(const float *mass,
			      const float (*pos)[3],
			      const float (*vel)[3],
			      const float *rho,
			      const float *temp,
			      const float *hsmooth,
			      const float *metals,
			      size_t       size);

int tipsy_write_blackhole_particles(const float *mass,
				    const float (*pos)[3],
				    const float (*vel)[3],
				    const float softening,
				    size_t      size);

