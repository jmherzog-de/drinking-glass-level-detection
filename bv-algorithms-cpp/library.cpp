#include "library.h"

//#define WIN32
#define OSX

Autoscale::Autoscale() {}

Autoscale::~Autoscale() {}

void Autoscale::Create_LookupTable(int t_min, int t_max) {

    float c_0 = 65535 / (t_max - t_min);
    float c_1 = -1.0 * t_min;
    int temp = 0;

    for(size_t i = 0; i < 65536; i++)
    {
        temp = c_0 * (i + c_1);
        if (temp > 65535)
            temp = 65535;
        else if (temp < 0)
            temp = 0;

        this->lookupTable[i] = (unsigned short)temp;
    }

    return;
}

void Autoscale::Apply_16Bit(unsigned short img[2048][2048]) {

    for(size_t i = 0; i < 2048; i++)
    {
        for (size_t j = 0; j < 2048; j++)
        {
            img[i][j] = this->lookupTable[img[i][j]];
        }
    }
    return;
}

#ifdef WIN32
extern "C"
{
__declspec(dllexport) Autoscale* createInstance() {

    return new Autoscale();
}

__declspec(dllexport) void createLookUpTable(Autoscale* instance, unsigned short t_min, unsigned short t_max){

    instance->Create_LookupTable(t_min, t_max);
}

__declspec(dllexport) void apply(Autoscale *instance, unsigned short array[2048][2048])
{
    instance->Apply_16Bit(array);
}
};
#endif

#ifdef OSX
extern "C"
{
Autoscale* createInstance() {

    return new Autoscale();
}

void createLookUpTable(Autoscale* instance, unsigned short t_min, unsigned short t_max){

    instance->Create_LookupTable(t_min, t_max);
}

void apply(Autoscale *instance, unsigned short array[2048][2048])
{
    instance->Apply_16Bit(array);
}
};
#endif