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

int tipsy_write_header(tipsy_header const*);
int tipsy_write_star_particles(tipsy_star_data const*);
int tipsy_write_dark_particles(tipsy_dark_data const*);
int tipsy_write_gas_particles(tipsy_gas_data const*);
int tipsy_write_blackhole_particles(tipsy_star_data const*);
