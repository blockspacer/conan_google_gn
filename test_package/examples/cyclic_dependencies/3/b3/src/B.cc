#include "B.h"
#include "C.h"

#include <iostream>

B::B(double val):
    _val(val),
    _c(nullptr)
{}

void B::SetC(C *c)
{
    _c = c;
    _c->Print();
}

void B::Print()
{
    std::cout << "Type:C val=" << _val << std::endl;
}