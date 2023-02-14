set name=PepPre
set arch=x86_64
set content=tmp\%arch%.Windows
set /p version=<%content%\%name%\VERSION
set out=tmp\release\%name%-%version%.%arch%.Windows
rmdir /s /q %out%
pyinstaller ui\%name%.py -Fwy -i ui\%name%.png --distpath %out% --workpath tmp\build
md %out%\content
xcopy /e /y %content%\ %out%\content\
del %name%.spec
