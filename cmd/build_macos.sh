content="tmp/$(uname -m).$(uname -s)"
out="tmp/release/PepPre-$(cat $content/PepPre/VERSION).$(uname -m).$(uname -s)"
rm -rf $out
pyinstaller ui/PepPre.py -Dwy -i ui/PepPre.png --distpath $out --workpath tmp/build
mkdir $out/PepPre.app/Contents/MacOS/content
cp -R $content/ $out/PepPre.app/Contents/MacOS/content/
rm -rf PepPre.spec $out/PepPre
