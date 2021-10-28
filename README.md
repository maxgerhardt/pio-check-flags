# PlatformIO Check Compiler Flags Example

## Description

Demonstrates the usage of an extra script and a special compilter invocation to get the active macros in a file.

E.g., if you have a file `project_config.h`

```cpp
#ifndef _PROJECT_CONFIG_H_
#define _PROJECT_CONFIG_H_

// select driver here
#define DRIVER_ILI9341 1
//#define DRIVER_ST7789 1

#endif /* _PROJECT_CONFIG_H_ */
```

And you want to check in an extra script which macro was active or not, this repo shows a way to do that.

# Inner workings

The script uses primarily `env.Execute()` to execute the C++ compiler (stored in `env.["CXX"]`) with the regular build flags given by the environment and saves the output to a file.

>xtensa-esp32-elf-g++ -DPLATFORMIO=50202 [..more macros..] -w -dM -E -x c++ "C:\Users\Max\temp\check_flags\src\project_config.h" > flags.txt

The file then contains all compiler-builtin macros and explicitly enabled macros.

```
#define __DBL_MIN_EXP__ (-1021)
#define __UINT_LEAST16_MAX__ 0xffff
#define __ATOMIC_ACQUIRE 2
#define __FLT_MIN__ 1.1754943508222875e-38F
#define __GCC_IEC_559_COMPLEX 0
#define PLATFORMIO 50202
[..]
#define DRIVER_ILI9341 1
#define __DEC128_MIN__ 1E-6143DL
[...]
```

The file is then read out line-by-line and put into a Python dictionary, the key being the macro name and the value being the macro name

The resulting dictionary can then be checked for the existance of a certain key, in the standard `if "KEY_NAME" in macros:` way.

# Limitations

The built-up command does not include any `-I` flags to the e.g. Arduino core, so the target header file musn't `#include <Arduino.h>`. There is commented-out code in the script to fix that in a brute-force way, that is, adds all items from `env["CPPPATH"]` as `-I` flags. However, this probably misses out on library includes if additional libararies are used.

It's best to keep the configuration header file *as simple as possible*, only defining the configuration macros in the most minimal way.

## Expected output

With the unmodified source code, one should get 

```
check_for_flags(["buildprog"], [".pio\build\esp32dev\firmware.bin"])
AFTER build!!
xtensa-esp32-elf-g++ -DPLATFORMIO=50202 -DARDUINO_ESP32_DEV -DESP32 -DESP_PLATFORM -DF_CPU=\""240000000L\"" -DHAVE_CONFIG_H -DMBEDTLS_CONFIG_FILE=\""mbedtls/esp_config.h\"" -DARDUINO=10805 -DARDUINO_ARCH_ESP32 -DARDUINO_VARIANT=\""esp32\"" -DARDUINO_BOARD=\""Espressif ESP32 Dev Module\"" -w -dM -E -x c++ "C:\Users\Max\temp\check_flags\src\project_config.h" > flags.txt
Parsed a total of 239 defines (explicit and implicitly set).
DRIVER_ILI9341 was defined!! With value: 1
echo Super special command here....
Super special command here....
```

At the end, showcasing that it was successfully detected that the `DRIVER_ILI9341` macro was defined (and also to which value it was defined).

# Usage in a different project

Copy the `check_flags.py` into the project and add it to the `extra_scripts` expression of your `platformio.ini`.

Adapt the logic in `check_flags.py` regarding the read-out file and the reaction to it accordingly.

```ini
extra_scripts =
   check_flags.py
```