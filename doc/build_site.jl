import Documenter

root = "doc"
out = joinpath(root, "build")
mkpath(out)
for file in ["index.html", "CNAME"]
    cp(joinpath(root, file), joinpath(out, file); force=true)
end

versions = readdir(joinpath(root, "log")) .|> VersionNumber
print(maximum(versions))
for v in versions
    dir = joinpath(out, "api", string(v))
    mkpath(dir)
    open(joinpath(dir, "headline"); write=true) do io
        if v == maximum(versions)
            write(io, "Welcome to use PepPre!")
        else
            write(io, "PepPre $(maximum(versions)) Available!\nPlease visit http://peppre.ctarn.io to upgrade.")
        end
    end
end

Documenter.deploydocs(repo="github.com/ctarn/PepPre_bak.jl.git", versions=nothing)
