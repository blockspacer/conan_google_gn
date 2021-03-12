#include "B.h"
#include "A.h"

#include <iostream>

A::A(int val):
    _val(val),
    _b(nullptr)
{}

void A::SetB(B *b)
{
    _b = b;
    _b->Print(); // COMPILER ERROR: C2027: use of undefined type 'B'
}

void A::Print()
{
    std::cout << "Type:A val=" << _val << std::endl;
}