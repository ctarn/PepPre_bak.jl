import Documenter

Documenter.makedocs(sitename="PepPre")
Documenter.deploydocs(
    repo="github.com/ctarn/PepPre_bak.jl.git",
    dirname="doc",
    versions=["stable" => "v^", "v#.#", devurl => devurl],
)
