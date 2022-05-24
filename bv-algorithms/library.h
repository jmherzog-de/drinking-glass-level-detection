#ifndef BV_ALGORITHMS_LIBRARY_H
#define BV_ALGORITHMS_LIBRARY_H

#include <stdint.h>

class Autoscale
{

    uint16_t lookupTable[65536] = {0 };

public:

    Autoscale();

    ~Autoscale();

    void Create_LookupTable(int t_min, int t_max);

    void Apply_16Bit(unsigned short img[2048][2048]);

};
#endif