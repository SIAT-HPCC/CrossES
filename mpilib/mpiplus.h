#pragma once
#pragma once

#include <mpi.h>
#include <string.h>
#include <string>
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <stdlib.h>
#include <vector>
#include <time.h>
#include <fstream>

//（Python call)
long getExchange(MPI_Comm comm, int nowitera, double* replica_state, int state_size, long* paramlist, int param_size, int ex_kind, int md_kind);

//master 
long master(MPI_Comm comm, int nowitera, double* replica_state, int state_size, long*& paramlist, int ex_kind, int md_kind);

// replica send states to master 
long replica(MPI_Comm comm, double* replica_state, int state_size);

//change the paramlist
void exchange(long*& paramlist, std::vector<std::pair<int, int> > ex_partner_id);

// get replica pairs that need to exchange  , return the exchange pair by "ex_partner_id"
void acceptance_exchange(double* states, int state_size, std::vector<std::pair<int, int> > partners, std::vector<std::pair<int, int> >& ex_partner_id, int md_kind);

//calculate the exchange probability ,if ok return true, else returen false.
bool get_acceptance(double* a, double* b, std::string &acceptance_info);

void writeinfo(int nowitera, std::string ex_info,std::string acceptance_info);
void readinfo(int& nowitera, std::vector<std::pair<int, int> >& partners);

void init_states(double*& states, int s_size);
void init_partners(std::vector<std::pair<int, int> >& partners, int comm_size, int nowitera, int ex_kind);

