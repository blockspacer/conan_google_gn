#include "B.h"
#include "A.h"

#include <iostream>

B::B(double val):
    _val(val),
    _a(nullptr)
{}

void B::SetA(A *a)
{
    _a = a;
    _a->Print();
}

void B::Print()
{
    std::cout << "Type:B val=" << _val << std::endl;
}