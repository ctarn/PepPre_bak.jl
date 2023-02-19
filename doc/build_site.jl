import LibGit2

import Documenter

repo = "github.com/ctarn/PepPre_bak.jl.git"

root = "html"
out = joinpath(root, "build")

rm(out; force=true, recursive=true)
LibGit2.clone("https://$(repo)", out, branch="gh-pages")
rm(joinpath(out, ".git"); force=true, recursive=true)

for file in ["CNAME", "fig"]
    cp(joinpath(root, file), joinpath(out, file); force=true)
end

versions = readdir(joinpath(root, "log")) .|> VersionNumber
sort!(versions; rev=true)
logs = map(versions) do v in
    return "<li> version $(v):$(read(joinpath(root, "log", string(v)), String))</li>"
end

html = read(joinpath(root, "index.html"), String)
html = replace(html, "{{ release }}" => "<ul>$(join(logs))</ul>")
open(io -> write(io, html), joinpath(out, "index.html"); write=true)

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
