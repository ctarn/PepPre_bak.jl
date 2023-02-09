set arch=x86_64
set content=tmp\%arch%.Windows
set /p version=<%content%\PepPre\VERSION
set out=tmp\release\PepPre-%version%.%arch%.Windows
rmdir /s /q %out%
pyinstaller ui\PepPre.py -Fwy -i ui\PepPre.png --distpath %out% --workpath tmp\build
md %out%\content
xcopy /e /y %content%\ %out%\content\
del PepPre.spec
