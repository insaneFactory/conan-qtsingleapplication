from conans import ConanFile, RunEnvironment, VisualStudioBuildEnvironment, tools
import os
import shutil
import itertools
import codecs


class QtConan(ConanFile):
	name = "qtsingleapplication"
	version = "2.6"
	description = "Qt is a cross-platform framework for graphical user interfaces."
	topics = ("conan", "qt", "ui")
	url = "https://github.com/insaneFactory/conan-qtsingleapplication"
	homepage = "https://github.com/qtproject/qt-solutions"
	license = "LGPL-3.0"
	generators = "qmake"
	settings = "os", "arch", "compiler", "build_type"
	options = {"shared": [True, False]}
	default_options = "shared=True"
	requires = "qt/5.13.2@bincrafters/stable"
	_source_subfolder = "source_subfolder/qtsingleapplication"

	def source(self):
		tools.get("https://github.com/qtproject/qt-solutions/archive/master.tar.gz")
		os.rename("qt-solutions-master", "source_subfolder")

	def build(self):
		# PRO file
		proconfig = [
			"CONFIG += conan_basic_setup\n",
			"include(../../conanbuildinfo.pri)\n"
		]

		profile = os.path.join(self._source_subfolder, "qtsingleapplication.pro")
		with codecs.open(profile, "r", encoding="utf8") as f:
			proconfig.extend(f.readlines())
		with codecs.open(profile, "w", encoding="utf8") as f:
			f.write("".join(proconfig))

		# PRI file
		with codecs.open(os.path.join(self._source_subfolder, "config.pri"), "w", encoding="utf8") as f:
			if self.options.shared:
				f.write("SOLUTIONS_LIBRARY = yes")
		
		# Build
		if self.settings.compiler == "Visual Studio":
			env_build = VisualStudioBuildEnvironment(self)
			with tools.environment_append(env_build.vars):
				vcvars = tools.vcvars_command(self.settings)
				qmakecmd = os.path.join(self.deps_cpp_info["qt"].bin_paths[0], "qmake")
				self.run("%s && %s %s" % (vcvars, str(qmakecmd), self._source_subfolder))
				self.run("%s && nmake" % vcvars)
				self.run("%s && nmake install" % vcvars)
		else:
			env_build = RunEnvironment(self)
			with tools.environment_append(env_build.vars):
				self.run("qmake")
				self.run("make")
				self.run("make install")

	def package(self):
		srcpath = os.path.join(self._source_subfolder, "src")
		libpath = os.path.join(self._source_subfolder, "lib")
		self.copy("*.dll", dst="bin", src=libpath)
		self.copy("*.lib", dst="lib", src=libpath)
		self.copy("*.pdb", dst="lib", src=libpath)
		self.copy("*.so", dst="lib", src=libpath)
		self.copy("*.h", dst=os.path.join("include", self.name), src=srcpath)
		
	def package_info(self):
		self.cpp_info.libs = ["Qt5Solutions_SingleApplication-headd" if self.settings.build_type == "Debug" else "Qt5Solutions_SingleApplication-head"]
		self.cpp_info.defines = ["QT_QTSINGLEAPPLICATION_IMPORT"] if self.options.shared else []
