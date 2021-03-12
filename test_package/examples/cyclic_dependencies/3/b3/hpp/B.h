#ifndef __B_HPP__
#define __B_HPP__

class C;

class B
{
private:
    double _val;
    C* _c;

public:

    B(double val);

    void SetC(C *c);

    void Print();
};

#endif /* __B_HPP__ */