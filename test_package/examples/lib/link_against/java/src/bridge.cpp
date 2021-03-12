#include "java_bridge/bridge.hpp"

JNIEnv* create_vm()
{
    JavaVM* jvm;
    JNIEnv* env;
    JavaVMInitArgs args;
    const int JVM_OPTIONS_NB = 0;
    //JavaVMOption options[JVM_OPTIONS_NB];

    args.version = JNI_VERSION_1_8;
    args.nOptions = JVM_OPTIONS_NB;
    //options[0].optionString = "-ms1m";
    //options[0].optionString = "-mx1m";
    args.options = nullptr;//options;
    args.ignoreUnrecognized = JNI_FALSE;

    JNI_CreateJavaVM(&jvm, (void **)&env, &args);
    return env;
}
