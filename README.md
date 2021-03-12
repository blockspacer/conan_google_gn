# About

## Local build

```bash
export PKG_NAME=google_gn/e0358b49272c8b354eda0a595e1d7887343fab27@conan/stable
conan remove $PKG_NAME
conan create . conan/stable -s build_type=Debug --profile clang --build missing
```