import sys, os, re, stat, json, fnmatch, platform, glob, traceback, shutil
from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment, RunEnvironment, python_requires
from conans.errors import ConanInvalidConfiguration, ConanException
from conans.model.version import Version
from conans.tools import os_info
from functools import total_ordering

# if you using python less than 3 use from distutils import strtobool
from distutils.util import strtobool

conan_build_helper = python_requires("conan_build_helper/[~=0.0]@conan/stable")

class GnConan(conan_build_helper.CMakePackage):
    name = "google_gn"
    version = "master"
    license = "MIT"
    url = "https://gn.googlesource.com/gn/"
    description = "GN is a meta-build system that generates build files for Ninja."
    topics = ("gn", "google")
    settings = "os", "compiler", "arch"

    options = {
        "tests": [True, False],
        "use_gold_linker": [True, False]
    }

    default_options = {
        "tests": True,
        "use_gold_linker": False
    }

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

    def source(self):
        git = tools.Git(folder="gn")
        git.clone("https://gn.googlesource.com/gn/", self.version)

    def build_requirements(self):
        self.build_requires("ninja_installer/1.9.0@bincrafters/stable")

    def build(self):
        out_dir_path="out"
        if self.settings.os == "Windows":
            build_env = tools.vcvars_dict(self.settings)
        else:
            # GNU binutils's ld and gold don't support Darwin (macOS)
            # Use the default provided linker
            build_env = dict()
            if self.settings.os == "Linux":
                if self.options.use_gold_linker:
                    build_env["LDFLAGS"] = "-fuse-ld=gold"
        with tools.environment_append(build_env):
            with tools.chdir('%s/gn' % (self.source_folder)):
                python_executable = sys.executable
                self.run("{python} build/gen.py"\
                        .format(python=python_executable))
                self.run("ninja -j {cpu_nb} -C {build_dir}"\
                        .format(cpu_nb=tools.cpu_count()-1, build_dir=out_dir_path))
                if self.options.tests:
                    self.run("{build_dir}/gn_unittests".format(build_dir=out_dir_path))

    def package(self):
        bin_source_path = os.path.join(self.source_folder, "gn", "out")
        gn_executable = "gn.exe" if self.settings.os == "Windows" else "gn"
        self.copy(gn_executable, dst="bin", src=bin_source_path, keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
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
    