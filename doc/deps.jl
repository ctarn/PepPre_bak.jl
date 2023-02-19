using Pkg

deps = [
    PackageSpec(url="http://github.com/ctarn/MesCore.jl"),
    PackageSpec(url="http://github.com/ctarn/PepIso.jl"),
    PackageSpec(path=pwd()),
]
Pkg.develop(deps)
Pkg.resolve()
Pkg.instantiate()
