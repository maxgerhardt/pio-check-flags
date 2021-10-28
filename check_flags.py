Import("env")
from SCons.Script import COMMAND_LINE_TARGETS
import os
from typing import Dict

# don't do anything if the IDE is just trying to get metadata
if "idedata" in COMMAND_LINE_TARGETS:
    env.Exit(0)

def get_active_defines_for_file(env, src_file) -> Dict[str, str]:
    # invoke C++ compiler to get evaluated flags 
    # we build the command from scratch -- we include all flags that a normal
    # compiling invocation should have all original build flags.
    #print(env.Dump())
    build_flags = env.get('CPPDEFINES')
    cmd = ["$CXX"]
    for s in build_flags:
        if isinstance(s, tuple):
            # strings need special escpaing
            if isinstance(s[1], str):
                cmd += ['-D' + s[0] + '=\\""' + str(s[1]).replace("\\", "").replace("\"", "") + '\\""']
            else:
                cmd += ['-D' + s[0] + '=' + str(s[1])]
        else:
            cmd += ['-D' + s]
    # add include paths (so that the config file can e.g. find / include Arduino.h if it wants to)
    # spams a lot of "-I" flags though
    #for i in env.get("CPPPATH"):
    #    cmd += ['-I"' + i + '"']
    cmd += ['-w -dM -E -x c++']
    # last argument is the path to the file we want to parse
    cmd += ["\"" + src_file + "\""]
    cmd = ' '.join(cmd)
    # excute command, redirect output into a file (otherwise we can't get the output)
    retcode = env.Execute(cmd + " > flags.txt")
    if retcode != 0:
        print("Failure when executing extraction command.")
        env.Exit(-1)
    # read back file
    fp = open("flags.txt", 'r')
    define_lines = fp.readlines()
    fp.close()
    # parse macros from file
    macros = dict()
    for definition in define_lines:
        #print(definition)
        feature = definition[8:].strip().split(' ')
        macro_name, macro_val = feature[0], ' '.join(feature[1:])
        macros[macro_name] = macro_val
    print("Parsed a total of %d defines (explicit and implicitly set)." % len(macros))
    # cleanup file
    if os.path.isfile("flags.txt"):
        os.remove("flags.txt")
    # return macros
    return macros

def check_for_flags(source, target, env):
    print("AFTER build!!")
    # last argument is the path to the file we want to parse, in src/project_config.h
    # might also put it in PROJECT_INCLUDE_DIR
    src_file = os.path.join("$PROJECT_SRC_DIR", "project_config.h")
    macros = get_active_defines_for_file(env, src_file)

    # react on parsed macros
    if "DRIVER_ILI9341" in macros:
        print("DRIVER_ILI9341 was defined!! With value: " + macros["DRIVER_ILI9341"])
        env.Execute("echo Super special command here....")
    elif "DRIVER_ST7789" in macros:
        print("DRIVER_ST7789 was defined!! With value: " + macros["DRIVER_ST7789"])
    else:
        print("Neither DRIVER_ILI9341 or DRIVER_ST7789 was defined! :(")

# Add post action after build (if the firmware.elf changes)
env.AddPostAction("buildprog", check_for_flags)
