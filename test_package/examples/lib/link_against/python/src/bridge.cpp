#include "python_bridge/bridge.hpp"

Py_Dummy::Py_Dummy():
    _module("dummy"),
    _functions()
{
    _functions.insert(std::make_pair("multiply", py::PyFunc(_module, "multiply")));
}

long Py_Dummy::multiply(long a, long b)
{
    auto _a = py::PyInt(a), _b = py::PyInt(b);
    auto args = py::PyTuple(_a, _b);
    return _functions["multiply"].call(args).to_long();
}
