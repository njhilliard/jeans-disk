#pragma once

typedef struct {
	double time;
	int nbodies;
	int ndim;
	int ngas;
	int ndark;
	int nstar;
} tipsy_header;

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
	float *mass;
	float (*pos)[3];
	float (*vel)[3];
	float *rho;
	float *temp;
	float *metals;
	float *hsmooth;
	float *phi;
	float soft;
	size_t size;
} tipsy_gas_data;

typedef struct {
	float *mass;
	float (*pos)[3];
	float (*vel)[3];
	float *phi;
	float soft;
	size_t size;
} tipsy_dark_data;

typedef struct {
	float *mass;
	float (*pos)[3];
	float (*vel)[3];
	float *metals;
	float *tform;
	float *phi;
	float soft;
	size_t size;
} tipsy_star_data;

typedef struct {
	float *mass;
	float (*pos)[3];
	float (*vel)[3];
	float *phi;
	float soft;
	size_t size;
} tipsy_blackhole_data;
