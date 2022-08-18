#include "mpiplus.h"
#include <random>
#include <stdarg.h>
//#define DEBUG
//#undef DEBUG
static int MyDebugPrintf(const char* format, ...)
{
	va_list argPtr;
	int     count;
	FILE*   fp;
	va_start(argPtr, format);                  /*  获取可变参数列表  */
	fflush(stdout);                            /*  强制刷新输出缓冲区  */
	fp = fopen("debug.log","a");
	count = vfprintf(fp, format, argPtr);  /*  将信息输出到标准输出流设备stdout  ，错误流为stderr*/
	fclose(fp);
	va_end(argPtr);                            /*  可变参数列表结束  */
}

#ifdef DEBUG   /*  如果定义了插桩信息宏，就将调试信息指向调试函数  */
#define DebugPrintf  MyDebugPrintf

#else           /*  如果未定义插桩信息宏，那么就将调试信息指向空NOP  */
#define DebugPrintf

#endif

void init_states(double*& states, int s_size)
{
	states = (double*)malloc(s_size * sizeof(double));
	if (states == NULL) {
		throw "states malloc error!!";
		return;
		// 如何报错
	}
}
void init_partners(std::vector<std::pair<int, int> >& partners, int comm_size, int nowitera, int ex_kind)
{
	/*
	  init the exchange partners, odd exchange or even exchange

	  * partners: save the exchange partners
	  * comm_size: size of partners
	  * isodd: odd exchange or even exchange
	  * ex_kind: exchange kind

	*/
	bool  isodd = nowitera % 2;
	partners.clear();
	//DebugPrintf("C++ pre partner %d :", isodd);
	if (ex_kind == 1) {
		for (int i =  nowitera % 2; i < comm_size - 1; i += 2) {
			partners.push_back(std::make_pair(i, i + 1));
				//DebugPrintf("(%d,%d) ", i, i + 1);
		}
			//DebugPrintf("end \n");
	}
	else if (ex_kind == 2) {
		throw "Exchange kind not exist!";
		return;
	}
	else {
		throw "Exchange kind not exist!";
		return;
	}
}
void init_partners_v2(std::vector<std::pair<int, int> >& partners, int comm_size, int nowitera, int ex_kind, long* paramlist )
{
	/*
 * 	  init the exchange partners, odd exchange or even exchange
 *
 * 	  	  * partners: save the exchange partners
 * 	  	  	  * comm_size: size of partners
 * 	  	  	  	  * isodd: odd exchange or even exchange
 * 	  	  	  	  	  * ex_kind: exchange kind
 *
 * 	  	  	  	  	  	*/
	partners.clear();
	int* map_paramlist;
	map_paramlist = (int*)malloc(comm_size * sizeof(int));
	for (int i = 0; i < comm_size; i++) {
		map_paramlist[paramlist[i]] = i;
	}
	DebugPrintf("DEBUG[c++]:(%d) first ex partner is T( %d - %d) \n", nowitera, nowitera % 2, (nowitera % 2 + 1));
	if (ex_kind == 1) {
		for (int i = nowitera % 2; i < comm_size - 1; i += 2) {
			partners.push_back(std::make_pair(map_paramlist[i], map_paramlist[i + 1]));
			
		}
		free(map_paramlist);
	}
	else if (ex_kind == 2) {
		free(map_paramlist);
		throw "Exchange kind not exist!";
		return;
	}
	else {
		free(map_paramlist);
		throw "Exchange kind not exist!";
		return;
	}
}
long getExchange(MPI_Comm comm, int nowitera, double* replica_state, int state_size, long* paramlist, int param_size, int ex_kind, int md_kind) {

	int  comm_rank;
	long idx;
	MPI_Comm_rank(comm, &comm_rank);

	if (comm_rank == 0) {
		idx = master(comm, nowitera, replica_state, state_size, paramlist, ex_kind, md_kind);

	}
	else {
		idx = replica(comm, replica_state, state_size);
	}
	return idx;
}
#include <sstream>
template<typename T> std::string toString(const T& t)
{
	std::ostringstream oss;  //创建一个格式化输出流
	oss << t;             //把值传递如流中
	return oss.str();
}
long master(MPI_Comm comm, int nowitera, double* replica_state, int state_size, long*& paramlist, int ex_kind, int md_kind)
{
	/*
	  master in python call this method

	  * n_iterations:
	  * state_size： exchangesize
	  * ex_kind: exchange with who
	  * md_kind: md/mc ? md+mc
	*/
	double* states; //
	int s_size, comm_size, comm_rank, n_replica;
	long idx;
	std::string ex_info, acceptence_info;
	std::vector<std::pair<int, int> > partners; //(a,b) try to ex
	std::vector<std::pair<int, int> > ex_partner_id;//(a,b) need to ex 
	MPI_Comm_size(comm, &comm_size);
	MPI_Comm_rank(comm, &comm_rank);

	/*init parameter list*/
	DebugPrintf("DEBUG[c++]: master get size=%d, function is %d, %d, %d, %d\n", comm_size, nowitera, state_size, ex_kind, md_kind);

	s_size = state_size * comm_size;
	init_states(states, s_size);
	/*init partners*/
	//init_partners(partners, comm_size, nowitera, ex_kind);
        init_partners_v2(partners, comm_size, nowitera, ex_kind, paramlist);
	/*gather states;*/
	MPI_Gather(replica_state, state_size, MPI_DOUBLE, states, state_size, MPI_DOUBLE, 0, comm);
    
#ifdef DEBUG 
	DebugPrintf("DEBUG[c++]:(%d) preparamlist = ", nowitera);
	for (int i = 0; i < comm_size; i++) {
		DebugPrintf("%d ", paramlist[i]);
	}
	DebugPrintf("\nDEBUG[c++]:(%d) states = ", nowitera);
	for (int i = 0; i < s_size; i++) {
		DebugPrintf("%f ", states[i]);		
	}
	DebugPrintf("\n");
#endif

	/*判断交换*/
	//acceptance_exchange(states, state_size, partners, ex_partner_id, md_kind); 直接将函数代码拿出来了，不想传那么多参数了
	 

	ex_partner_id.clear();
	if(nowitera == 0)
           srand((time(NULL)));
	//DebugPrintf("DEBUG: now in accc  size is %d , md_kind is \n", partners.size(), md_kind);
	for (int i = 0; i < partners.size(); i++) {
		int a = partners[i].first, b = partners[i].second;
		if (md_kind == 1) {
			DebugPrintf("DEBUG[c++]: now judge (%d,%d): \n", a, b);
			bool acc = get_acceptance(states + (a * state_size), states + (b * state_size), acceptence_info); //  // 
			//printf("%d with %d is %d\n", a, b, acc);
			//acc = true;
			if (acc) {
				ex_partner_id.push_back(std::make_pair(a, b));
				ex_info.append("  " + toString(a) + "  x  " + toString(b) + "  ");
			}
			else {
				ex_info.append("  " + toString(a) + "    " + toString(b) + "  ");
			}
		}
		else {
			throw "The kind of md is error!\n";
		}
	}
	// gromacs md.log 信息
	if (nowitera % 2 == 0)
		ex_info.insert(0, "Repl ex  ");
	else {
		ex_info.insert(0, "Repl ex   0  ");
		ex_info.append("  " + toString(comm_size - 1));
	}
	acceptence_info.insert(0, "Repl pr  ");

#ifdef DEBUG 
	DebugPrintf("DEBUG[c++]:(%d) ", nowitera);
	for (int i = 0; i < ex_partner_id.size(); i++) {
		DebugPrintf("ex(%d,%d) ", ex_partner_id[i].first, ex_partner_id[i].second);
	}
	DebugPrintf("\nDEBUG[c++]:(%d) exsize is %d now is exchange\n", nowitera, ex_partner_id.size());
#endif

	/*交换*/
	exchange(paramlist, ex_partner_id);

#ifdef DEBUG 
	DebugPrintf("DEBUG[c++]:(%d) now newparamlist = ", nowitera);
	for (int i = 0; i < comm_size; i++) {
		DebugPrintf("%d ", paramlist[i]);
	}
	DebugPrintf("\n");
#endif

	//分配 paramlist idx
	MPI_Scatter(paramlist, 1, MPI_LONG, &idx, 1, MPI_LONG, 0, comm);

	writeinfo(nowitera,  ex_info, acceptence_info);

	free(states);
	partners.clear();
	ex_partner_id.clear();

	return idx;
}

long replica(MPI_Comm comm, double* replica_state, int state_size)
{
	/*
	   replica send states to master （Python call)
	*/
	int* paramlist = NULL;
	long idx;
	double* states = NULL;
	int  comm_rank;
	MPI_Comm_rank(comm, &comm_rank);
	//printf("C++ now task %d gather\n",comm_rank);
	MPI_Gather(replica_state, state_size, MPI_DOUBLE, states, state_size, MPI_DOUBLE, 0, comm);

	//
	MPI_Scatter(paramlist, 1, MPI_LONG, &idx, 1, MPI_LONG, 0, comm);
	//printf("C++ now task %d get param = %ld\n", comm_rank, idx);
	return idx;
}




void exchange(long*& paramlist, std::vector<std::pair<int, int> > ex_partner_id)
{
	/*
	  exchange the paramlist id between exchange partners

	  * paramlist:
	  * ex_partner_id:
	*/
	for (int i = 0; i < ex_partner_id.size(); i++) {
		int a = ex_partner_id[i].first, b = ex_partner_id[i].second;
		int tmp;
		tmp = paramlist[a];
		paramlist[a] = paramlist[b];
		paramlist[b] = tmp;
	}
}


void acceptance_exchange(double* states, int state_size, std::vector<std::pair<int, int> > partners, std::vector<std::pair<int, int> >& ex_partner_id, int md_kind)
{
	/*
	  get replica pairs that need to exchange ，return the exchange pair by "ex_partner_id"

	  * states: all replicas states
	  * state_size:
	  * partners: the id pair of exchange replica partners
	  * ex_partner_id: the relica need to exchange
	  * md_kind:

	*/
	ex_partner_id.clear();
	//DebugPrintf("DEBUG: now in accc  size is %d , md_kind is \n", partners.size(), md_kind);
	for (int i = 0; i < partners.size(); i++) {
		int a = partners[i].first, b = partners[i].second;
		if (md_kind == 1) {
			DebugPrintf("DEBUG[c++]: now judge (%d,%d): \n", a, b);
			/* bool acc = get_acceptance(states + (a * state_size), states + (b * state_size)); //  // 
			//printf("%d with %d is %d\n", a, b, acc);
			//acc = true;
			if (acc) {
				ex_partner_id.push_back(std::make_pair(a, b));
			}*/
		}
		else {
			throw "The kind of md is error!\n";
		}
	}

}

bool get_acceptance(double* state_a, double* state_b, std::string &acceptance_info)
{
	/*
	  calculate the exchange probability ,if ok return true, else returen false.

	  * state_a: state of replica A
	  * state_b:

	  return whether or not to exchange

	*/
	double ua = state_a[0], ub = state_b[0], ta = state_a[1], tb = state_b[1], r = 8.3138462;
	//double delta = ua / (r * tb) + ub / (r * ta) - ua / (r * ta) - ub / (r * tb);
	//delta = -delta;
	//delta *= 1000;
	double delta = ((ua - ub) * (1 / (r * ta) - 1 / (r * tb))) * 1000;
	double randx = rand() / double(RAND_MAX);
	double pr = exp(delta);
	acceptance_info.append(" " + toString(pr));
	DebugPrintf("            ua = %f,ta= %f,ub= %f, tb= %f\n            randx = %f < exp(%f) = %f ?\n",  ua, ta, ub, tb, randx, delta, exp(delta));
	if (delta >= 0.0 || randx < pr)
		return true;
	else
		return false;
}

void writeinfo(int nowitera, std::string ex_info, std::string acceptance_info)
{
	/*

	*/
	std::ofstream outfile("md.log", std::ios::app);
	if (!outfile.is_open())
	{
		throw "Outfile can't open!";
	}
	//DebugPrintf("now write\n");
	outfile << ex_info;
	outfile << std::endl;
	outfile << acceptance_info;
	outfile << std::endl  << std::endl;
	outfile.close();

}
