#ifndef __JAVA_BRIDGE_HPP__
#define __JAVA_BRIDGE_HPP__

#include <jni.h>


#if defined(_MSC_VER)

# ifdef JAVA_BRIDGE_EXPORTS
#  define JAVA_BRIDGE_API __declspec(dllexport)
# else
#  define JAVA_BRIDGE_API __declspec(dllimport)
# endif
#else
# define JAVA_BRIDGE_API
#endif

JAVA_BRIDGE_API JNIEnv* create_vm();

#endif
