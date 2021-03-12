#include "python_bridge/internals.hpp"

#include <memory>
#include <utility>

namespace py {

    PyException::PyException(std::string const& msg)
        : _msg(msg)
    {}

    const char* PyException::what() const NOEXCEPT
    {
        return _msg.c_str();
    }

    PyObj::PyObj():
        _obj(nullptr)
    {}

    PyObj::PyObj(PyObject* obj):
        _obj(obj)
    {}

    PyObj::PyObj(const PyObj& other):
        _obj(other._obj)
    {
        Py_XINCREF(this->_obj);
    }

    PyObj& PyObj::operator=(const PyObj& other)
    {
        Py_XDECREF(this->_obj);
        this->_obj = other._obj;
        Py_XINCREF(this->_obj);
        return *this;
    }

    PyObj::PyObj(PyObj&& other)
    {
        this->_obj = std::move(other._obj);
        other._obj = nullptr;
    }

    PyObj& PyObj::operator=(PyObj&& other)
    {
        this->_obj = std::move(other._obj);
        other._obj = nullptr;
        return *this;
    }

    PyObj::~PyObj()
    {
        Py_XDECREF(this->_obj);
    }

    PyObj::operator PyObject*() const
    {
        return this->_obj;
    }

    PyObject* PyObj::steal()
    {
        auto* stolen = this->_obj;
        this->_obj = nullptr;
        return stolen;
    }

    /* Language types */
    PyString::PyString(const std::string& str):
        PyObj()
    {
        this->_obj = PyString_FromString(str.c_str());
    }

    PyInt::PyInt(long value):
        PyObj()
    {
        this->_obj = PyInt_FromLong(value);
    }

    /* Utilities */
    PyModule::PyModule(const std::string& name):
        PyObj()
    {
        this->_obj = PyImport_Import(PyString(name));
        if (!this->_obj) {
            PyErr_Print();
            throw PyException("Failed to load \"" + name + "\"");
        }
    }

    PyVariadic::PyVariadic(PyObject* variadic):
        PyObj(variadic)
    {}

    long PyVariadic::to_long() const
    {
        return PyInt_AsLong(this->_obj);
    }

    PyFunc::PyFunc(const PyModule& module, const std::string& funcname):
        PyObj()
    {
        this->_obj = PyObject_GetAttrString(module, funcname.c_str());
        if (!this->_obj || !PyCallable_Check(this->_obj)) {
            if (PyErr_Occurred()) {
                PyErr_Print();
            }
            throw PyException("Cannot find function \"" + funcname + "\"");
        }
    }

    PyVariadic PyFunc::call(const PyTuple& args) const
    {
        auto* pValue = PyObject_CallObject(this->_obj, args);
        if (!pValue) {
            PyErr_Print();
            throw PyException("Call failed");
        }
        return PyVariadic(pValue);
    }

    namespace {

        class PythonAPI
        {
            public:
                PythonAPI() { Py_Initialize(); }
                ~PythonAPI() { Py_Finalize(); }
        };

        PythonAPI py_api;
    }

} // namespace py
