"""
Distutils doesn't support nasm, so this is a custom compiler for NASM
"""

from distutils.msvc9compiler import MSVCCompiler
from distutils.sysconfig import get_config_var
import sys


class WinNasmCompiler(MSVCCompiler) :
    compiler_type = 'nasm'
    src_extensions = ['.asm']
    obj_extension = '.obj'
    language_map = {".asm"   : "asm",}
    language_order = ["asm"]
    executables = {'preprocessor' : None,
               'compiler'     : ["nasm"],
               'compiler_so'  : ["nasm"],
               'compiler_cxx' : ["nasm"],
               'linker_so'    : ["cc", "-shared"],
               'linker_exe'   : ["cc", "-shared"],
               'archiver'     : ["ar", "-cr"],
               'ranlib'       : None,
               }
    def __init__ (self,
                  verbose=0,
                  dry_run=0,
                  force=0):

        MSVCCompiler.__init__ (self, verbose, dry_run, force)
        self.set_executable("compiler", "nasm")

    def _is_gcc(self, compiler_name):
        return False  # ¯\_(ツ)_/¯

    def _get_cc_args(self, pp_opts, debug, before):
        if sys.platform == 'darwin':
            # Fix the symbols on macOS
            cc_args = pp_opts + ["-f macho64","-DNOPIE","--prefix=_"]
        elif sys.platform == "win32":
            cc_args = pp_opts + ["-f win64", "-DWINDOWS", "-DNOPIE"]
        else:
            # Use 64-bit elf format for Linux
            cc_args = pp_opts + ["-f elf64"]
        if debug:
            # Debug symbols from NASM
            cc_args[:0] = ['-g']
        if before:
            cc_args[:0] = before
        return cc_args

    def link(self, target_desc, objects,
             output_filename, output_dir=None, libraries=None,
             library_dirs=None, runtime_library_dirs=None,
             export_symbols=None, debug=0, extra_preargs=None,
             extra_postargs=None, build_temp=None, target_lang=None):
        # Make sure libpython gets linked
        if not self.runtime_library_dirs:
            if sys.platform == 'win32':
                self.runtime_library_dirs.append(get_config_var('LIBDEST'))
            else:
                self.runtime_library_dirs.append(get_config_var('LIBDIR'))
        if not self.libraries and sys.platform in ('linux', 'darwin'):
            libraries = ["python" + get_config_var("LDVERSION")]
        if not extra_preargs:
            extra_preargs = []

        return super().link(target_desc, objects,
                            output_filename, output_dir, libraries,
                            library_dirs, runtime_library_dirs,
                            export_symbols, debug, extra_preargs,
                            extra_postargs, build_temp, target_lang)

    def runtime_library_dir_option(self, dir):
        if sys.platform == "darwin":
            return "-L" + dir
        elif sys.platform == "win32":
            return "-L" + dir
        else:
            return "-Wl,-R" + dir
