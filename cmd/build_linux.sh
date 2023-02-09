content="tmp/$(uname -m).$(uname -s)"
out="tmp/release/PepPre-$(cat $content/PepPre/VERSION).$(uname -m).$(uname -s)"
rm -rf $out
pyinstaller ui/PepPre.py -Fwy -i ui/PepPre.png --distpath $out --workpath tmp/build
mkdir $out/content
cp -R $content/* $out/content/
rm -rf PepPre.spec
