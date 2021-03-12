#include "C.h"
#include "A.h"

#include <iostream>

C::C(int val):
    _val(val),
    _a(nullptr)
{}

void C::SetA(A *a)
{
    _a = a;
    _a->Print(); // COMPILER ERROR: C2027: use of undefined type 'A'
}

void C::Print()
{
    std::cout << "Type:A val=" << _val << std::endl;
}