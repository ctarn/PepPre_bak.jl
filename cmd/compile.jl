import PackageCompiler
import Pkg
import TOML

rm("Manifest.toml", force=true)

cfg = TOML.parsefile("Project.toml")

paths = ["../MesCore.jl", "../PepIso.jl"]
Pkg.develop([Pkg.PackageSpec(path=path) for path in paths])

dir = "tmp/$(Sys.ARCH).$(Sys.iswindows() ? "Windows" : Sys.KERNEL)/$(cfg["name"])"

PackageCompiler.create_app(".", dir;
    force=true, include_lazy_artifacts=true, include_transitive_dependencies=true,
)

open(joinpath(dir, "VERSION"); write=true) do io
    write(io, cfg["version"])
end
