import LibGit2

import Documenter

repo = "github.com/ctarn/PepPre_bak.jl.git"

root = "doc"
out = joinpath(root, "build")

rm(out; force=true, recursive=true)
LibGit2.clone("https://$(repo)", out, branch="gh-pages")
rm(joinpath(out, ".git"); force=true, recursive=true)

for file in ["index.html", "CNAME", "fig"]
    cp(joinpath(root, file), joinpath(out, file); force=true)
end

versions = readdir(joinpath(root, "log")) .|> VersionNumber
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

Documenter.deploydocs(repo=repo, versions=nothing)
