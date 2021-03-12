#ifndef __PYTHON_BRIDGE_INTERNALS_HPP__
#define __PYTHON_BRIDGE_INTERNALS_HPP__

#include "python_bridge/exports.hpp"

#include <Python.h>

#include <exception>
#include <string>

namespace py {

    class PYTHON_BRIDGE_API PyException:
        public std::exception
    {
        public:
            PyException(std::string const& msg="");
            virtual ~PyException() = default;
            PyException& operator=(const PyException& other) = default;
            virtual const char* what() const NOEXCEPT;

        private:
            std::string _msg;
    };

    class PYTHON_BRIDGE_API PyObj {
        public:
            PyObj();
            PyObj(PyObject* obj);
            PyObj(const PyObj& other);
            PyObj& operator=(const PyObj& other);
            PyObj(PyObj&& other);
            PyObj& operator=(PyObj&& other);

            ~PyObj();

            PyObject* steal();
            operator PyObject*() const;

        protected:
            PyObject* _obj;
    };

    /* Language types */
    class PYTHON_BRIDGE_API PyString:
        public PyObj
    {
        public:
            PyString(const std::string& str);
            ~PyString() = default;
    };

    class PYTHON_BRIDGE_API PyInt:
        public PyObj
    {
        public:
            PyInt(long value);
            ~PyInt() = default;
    };

    namespace internal {
        template <class T>
        void fill_PyTuple(PyObject* pyTuple, std::size_t i, T& value) {
            PyTuple_SetItem(pyTuple, i, value.steal());
        }

        template <class T, class... TArgs>
        void fill_PyTuple(PyObject* pyTuple, std::size_t i, T& value, TArgs&... values) {
            PyTuple_SetItem(pyTuple, i, value.steal());
            fill_PyTuple(pyTuple, i+1, values...);
        }
    } // namespace internal

    class PYTHON_BRIDGE_API PyTuple:
        public PyObj
    {
         public:
            template<class... TArgs>
            PyTuple(TArgs&... args):
                PyObj()
            {
                this->_obj = PyTuple_New(sizeof...(args));
                internal::fill_PyTuple(_obj, 0, args...);
            }
            ~PyTuple() = default;
    };

    /* Utilities */
    class PYTHON_BRIDGE_API PyModule:
        public PyObj
    {
        public:
            PyModule(const std::string& name);
            ~PyModule() = default;
    };

    class PYTHON_BRIDGE_API PyVariadic:
        public PyObj
    {
        public:
            PyVariadic(PyObject* variadic);
            ~PyVariadic() = default;

            long to_long() const;
    };

    class PYTHON_BRIDGE_API PyFunc:
        public PyObj
    {
        public:
            PyFunc() = default;
            PyFunc(const PyModule& module, const std::string& funcname);
            ~PyFunc() = default;

            PyVariadic call(const PyTuple& args) const;
    };

} // namespace py

#endif /*__PYTHON_BRIDGE_INTERNALS_HPP__*/
