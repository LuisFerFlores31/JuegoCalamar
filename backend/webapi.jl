include("pacman.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

route("/run") do
    run!(model, 1)

    pacmans = []
    ghosts = []

    for agent in allagents(model)
        if agent isa Pacman
            push!(pacmans, agent)
        elseif agent isa Ghost
            push!(ghosts, agent)
        end
    end

    visited = collect(model.visited_cells)

    json(Dict(
        :msg => "Simulación en curso",
        "pacmans" => pacmans,
        "ghosts" => ghosts,
        "visited" => visited,
        "matrix" => [collect(row) for row in eachrow(matrix)]
    ))
end

Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

up()
