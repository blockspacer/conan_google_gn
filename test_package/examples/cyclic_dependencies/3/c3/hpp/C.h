#ifndef __C_HPP__
#define __C_HPP__

class A;

class C
{
private:
    int _val;
    A *_a;

public:

    C(int val);

    void SetA(A *a);

    void Print();
};

#endif /* __C_HPP__ */