# About

## Local build

```bash
export PKG_NAME=google_gn/master@conan/stable
(CONAN_REVISIONS_ENABLED=1 \
    conan remove --force $PKG_NAME || true)
conan create . conan/stable -s build_type=Debug --profile clang --build missing
```
