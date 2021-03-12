# About

## Local build

```bash
export PKG_NAME=google_gn/master@conan/stable
conan remove $PKG_NAME
conan create . conan/stable -s build_type=Debug --profile clang --build missing
```