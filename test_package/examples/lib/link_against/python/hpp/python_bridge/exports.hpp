#ifndef __PYTHON_BRIDGE_EXPORTS_HPP__
#define __PYTHON_BRIDGE_EXPORTS_HPP__

#if defined(_MSC_VER)
# ifdef PYTHON_BRIDGE_EXPORTS
#  define PYTHON_BRIDGE_API __declspec(dllexport)
# else
#  define PYTHON_BRIDGE_API __declspec(dllimport)
# endif
#else
# define PYTHON_BRIDGE_API
#endif

#if !defined(HAS_NOEXCEPT)
#if defined(__clang__)
#if __has_feature(cxx_noexcept)
# define HAS_NOEXCEPT
#endif
#elif defined(__GXX_EXPERIMENTAL_CXX0X__) && __GNUC__ * 10 + __GNUC_MINOR__ >= 46 || \
      defined(_MSC_FULL_VER) && _MSC_FULL_VER >= 190023026
# define HAS_NOEXCEPT
#endif
#endif

#ifdef HAS_NOEXCEPT
#define NOEXCEPT noexcept
#else
#define NOEXCEPT
#endif

#endif /*__PYTHON_BRIDGE_EXPORTS_HPP__*/
