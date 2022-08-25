import sys, os, re, stat, json, fnmatch, platform, glob, traceback, shutil
from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment, RunEnvironment, python_requires
from conans.errors import ConanInvalidConfiguration, ConanException
from conans.model.version import Version
from conans.tools import os_info
from functools import total_ordering
from contextlib import contextmanager
import os
import textwrap
import time
from six import StringIO  # Python 2 and 3 compatible

# if you using python less than 3 use from distutils import strtobool
from distutils.util import strtobool

required_conan_version = ">=1.33.0"

conan_build_helper = python_requires("conan_build_helper/[~=0.0]@conan/stable")

# Users locally they get the 1.0.0 version,
# without defining any env-var at all,
# and CI servers will append the build number.
# USAGE
# version = get_version("1.0.0")
# BUILD_NUMBER=-pre1+build2 conan export-pkg . my_channel/release
def get_version(version):
    bn = os.getenv("BUILD_NUMBER")
    return (version + bn) if bn else version

class GnConan(conan_build_helper.CMakePackage):
    name = "google_gn"
    version = get_version("master")
    license = "MIT"
    url = "https://gn.googlesource.com/gn/"
    description = "GN is a meta-build system that generates build files for Ninja."
    topics = ("gn", "google")
    settings = "os", "compiler", "arch", "build_type"

    options = {
        "tests": [True, False],
        "use_gold_linker": [True, False]
    }

    default_options = {
        "tests": True,
        "use_gold_linker": False
    }

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang_cl(self):
        return self.settings.compiler == 'clang' and self.settings.os == 'Windows'

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    @property
    def _minimum_compiler_version_supporting_cxx17(self):
        return {
            "Visual Studio": 15,
            "gcc": 7,
            "clang": 4,
            "clang-cl": 4,
            "apple-clang": 10,
        }.get(str(self.settings.compiler))

    def configure(self):
        #if self._is_clang_cl:
        #    raise ConanInvalidConfiguration("TODO: add clang_cl support")
            
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        else:
            if self._minimum_compiler_version_supporting_cxx17:
                if tools.Version(self.settings.compiler.version) < self._minimum_compiler_version_supporting_cxx17:
                    raise ConanInvalidConfiguration("gn requires a compiler supporting c++17")
            else:
                self.output.warn("gn recipe does not recognize the compiler. gn requires a compiler supporting c++17. Assuming it does.")

    @property
    def _source_subfolder(self):
        return "gn"

    @property
    def commit(self):
        return "4b613b106078d103e005f71d40d6456376a2e32d"

    @property
    def repo_url(self):
        return "https://gn.googlesource.com/gn/"

    def source(self):
        #git = tools.Git(folder="gn")
        #git.clone("https://gn.googlesource.com/gn/", self.version)
        self.run('git clone --progress --branch {} --single-branch --recursive --recurse-submodules {} {}'.format(self.version, self.repo_url, self._source_subfolder))
        #self.run('git clone --progress --depth 1 --branch {} --recursive --recurse-submodules {} {}'.format(self.version, self.repo_url, self._source_subfolder))        
        if self.commit:
            with tools.chdir(self._source_subfolder):
                self.run('git checkout {}'.format(self.commit))

    def build_requirements(self):
        #self.build_requires("ninja_installer/1.9.0@bincrafters/stable")
        self.build_requires("ninja/[>=1.11]")
        # FIXME: add cpython build requirements for `build/gen.py`.

    # known_platforms:
    # 'linux', 'darwin', 'mingw', 
    # 'msys', 'msvc', 'aix', 'fuchsia', 
    # 'freebsd', 'netbsd', 'openbsd', 
    # 'haiku', 'solaris', 'zos'
    def _to_gn_platform(self):
        if tools.is_apple_os(self.settings.os):
            return "darwin"
        if self._is_msvc or self._is_clang_cl:
            return "msvc"
        # Assume gn knows about the os
        return str(self.settings.os).lower()

    @contextmanager
    def _build_context(self):
        if self._is_msvc or self._is_clang_cl:
        #if self.settings.compiler == "Visual Studio":
            build_env = tools.vcvars_dict(self.settings)
            #build_env["CFLAGS"] += ' /DDUNICODE'
            #build_env["CFLAGS"] += ' /DDNOMINMAX'
            #build_env["CFLAGS"] += ' /DDWIN32_LEAN_AND_MEAN'
            #build_env["CFLAGS"] += ' /DD_UNICODE'
            #build_env["CFLAGS"] += ' /DD_HAS_EXCEPTIONS=0'
            #if self.settings.os != "Windows":
                # GNU binutils's ld and gold don't support Darwin (macOS)
                # Use the default provided linker
                # build_env = dict()
            #    if self.settings.os == "Linux":
            #        if self.options.use_gold_linker:
            #            build_env["LDFLAGS"] += " -fuse-ld=gold"
            #with tools.vcvars(self.settings):
            with tools.environment_append(build_env):
                yield
        else:
            compiler_defaults = {}
            if self.settings.compiler == "gcc":
                compiler_defaults = {
                    "CC": "gcc",
                    "CXX": "g++",
                    "AR": "ar",
                    "LD": "g++",
                }
            elif self.settings.compiler == "clang":
                compiler_defaults = {
                    "CC": "clang",
                    "CXX": "clang++",
                    "AR": "ar",
                    "LD": "clang++",
                }
            env = {}
            for k in ("CC", "CXX", "AR", "LD"):
                v = tools.get_env(k, compiler_defaults.get(k, None))
                if v:
                    env[k] = v
            #if self.settings.os == "Windows":
                # build_env = tools.vcvars_dict(self.settings)
                # pass
            
            if self.settings.os != "Windows":
                # GNU binutils's ld and gold don't support Darwin (macOS)
                # Use the default provided linker
                # build_env = dict()
                if self.settings.os == "Linux":
                    if self.options.use_gold_linker:
                        env["LDFLAGS"] = "-fuse-ld=gold"
            with tools.environment_append(env):
                yield

    def build(self):
        out_dir_path=os.path.join(self.build_folder, "gn", "out")

        with self._build_context():
            with tools.chdir('%s/gn' % (self.source_folder)):
                python_executable = sys.executable

                # Generate dummy header to be able to run `build/ben.py` with `--no-last-commit-position`. This allows running the script without the tree having to be a git checkout.
                tools.save(os.path.join(self.build_folder, "gn", "src", "gn", "last_commit_position.h"),
                           textwrap.dedent("""\
                                #pragma once
                                #define LAST_COMMIT_POSITION "1"
                                #define LAST_COMMIT_POSITION_NUM 1
                                """))
                conf_args = [
                    "--no-last-commit-position",
                    "--host={}".format(self._to_gn_platform()),
                ]
                if self.settings.build_type == "Debug":
                    conf_args.append("-d")
                self.run("{python} build/gen.py {cargs}".format(python=python_executable, cargs=" ".join(conf_args)), run_environment=True)
                # Try sleeping one second to avoid time skew of the generated ninja.build file (and having to re-run build/gen.py)
                time.sleep(1)
                build_args = [
                    "-C", out_dir_path,
                    "-j{}".format(max(1, tools.cpu_count()-2)),
                ]
                self.run("ninja {cargs}".format(cargs=" ".join(build_args)), run_environment=True)

                #self.run("{python} build/gen.py"\
                #        .format(python=python_executable))
                #self.run("ninja -j {cpu_nb} -C {build_dir}"\
                #        .format(cpu_nb=tools.cpu_count()-1, build_dir=out_dir_path))
                if self.options.tests:
                    mybuf = StringIO()
                    try:
                        # TODO: FormatTest fails on windows under clang-cl MTd
                        self.run("{build_dir}/gn_unittests --gtest_filter=-*FormatTest.*".format(build_dir=out_dir_path), output=mybuf)
                    except ConanException:
                        #self.run("gn_unittests", cwd=out_dir_path)
                        self.output.error(mybuf.getvalue())
                        raise
                    

    def package(self):
        bin_source_path = os.path.join(self.source_folder, "gn", "out")
        gn_executable = "gn.exe" if self.settings.os == "Windows" else "gn"
        self.copy(gn_executable, dst="bin", src=bin_source_path, keep_path=False)

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.bindirs = ['bin']

    def deploy(self):
        self.copy("*", keep_path=True)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "lib"))
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
        gn_executable = "gn.exe" if self.settings.os == "Windows" else "gn"
        self.env_info.GN_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", gn_executable))
        self.user_info.GN_BIN = self.env_info.GN_BIN
