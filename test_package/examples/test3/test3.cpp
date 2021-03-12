#include <gtest/gtest.h>

#include "java_bridge/bridge.hpp"
#include "python_bridge/bridge.hpp"

TEST(Test3, LinkAgainstJava)
{
    JNIEnv* jvm = create_vm();
    ASSERT_NE(jvm, nullptr);
    ASSERT_EQ(jvm->GetVersion(), 0x10008);
}

TEST(Test3, LinkAgainstPython)
{
    Py_Dummy my_python_module;
    ASSERT_EQ(my_python_module.multiply(2, 3), 6);
    ASSERT_EQ(my_python_module.multiply(-5, 10), -50);
    ASSERT_EQ(my_python_module.multiply(0, 10), 0);
}
