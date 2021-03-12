#ifndef __PYTHON_BRIDGE_BRIDGE_HPP__
#define __PYTHON_BRIDGE_BRIDGE_HPP__

#include "python_bridge/internals.hpp"

#include <map>

class PYTHON_BRIDGE_API Py_Dummy {
    public:
        Py_Dummy();
        ~Py_Dummy() = default;

        long multiply(long a, long b);

    private:
        py::PyModule _module;
        std::map<std::string, py::PyFunc> _functions;
};

#endif /*__PYTHON_BRIDGE_BRIDGE_HPP__*/
