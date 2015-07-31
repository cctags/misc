@echo off

set MINGW_PATH=C:\mingw
set C_INCLUDE_PATH=%MINGW_PATH%\include;%MINGW_PATH%\lib\gcc\mingw32\3.4.5\include
set CPLUS_INCLUDE_PATH=%MINGW_PATH%\include\c++\3.4.5;%MINGW_PATH%\include\c++\3.4.5\mingw32;%MINGW_PATH%\include\c++\3.4.5\backward;%C_INCLUDE_PATH%
set LIBRARY_PATH=%MINGW_PATH%\lib;%MINGW_PATH%\lib\gcc\mingw32\3.4.5

set PATH=%PATH%;%MINGW_PATH%\bin;%MINGW_PATH%\libexec\gcc\mingw32\3.4.5

@echo on
