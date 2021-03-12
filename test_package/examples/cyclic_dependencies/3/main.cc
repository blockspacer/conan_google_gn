#include "A.h"
#include "B.h"
#include "C.h"

#include <iostream>

int main(int argc, char* argv[])
{
    A a(10);
    B b(3.14);
    C c(5);
    a.Print();
    a.SetB(&b);
    b.Print();
    b.SetC(&c);
    c.Print();
    c.SetA(&a);
    return 0;
}