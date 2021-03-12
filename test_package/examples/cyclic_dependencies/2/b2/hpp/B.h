#ifndef __B_HPP__
#define __B_HPP__

class A;

class B
{
private:
    double _val;
    A* _a;

public:

    B(double val);

    void SetA(A *a);

    void Print();
};

#endif /* __B_HPP__ */