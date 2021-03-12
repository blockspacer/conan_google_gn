#ifndef __A_HPP__
#define __A_HPP__

class B;

class A
{
private:
    int _val;
    B *_b;

public:

    A(int val);

    void SetB(B *b);

    void Print();
};

#endif /* __A_HPP__ */