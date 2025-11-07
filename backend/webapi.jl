include("pacman.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

route("/run") do
    run!(model, 1)

    # Convertir los agentes a diccionarios con solo la información necesaria
    pacmans = [Dict(
        "id" => p.id,
        "pos" => p.pos,
        "captured" => p.captured
    ) for p in allagents(model) if p isa Pacman]

    ghosts = [Dict(
        "id" => g.id,
        "pos" => g.pos,
        "color" => g.color,
        "captured_pacman" => g.captured_pacman
    ) for g in allagents(model) if g isa Ghost]

    visited = collect(model.visited_cells)

    json(Dict(
        "pacmans" => pacmans,
        "ghosts" => ghosts,
        "visited" => visited,
        "matrix" => [collect(row) for row in eachrow(matrix)],
        "squids_won" => model.squids_won,
        "ghosts_won" => model.ghosts_won,
        "painted_cells" => model.painted_cells,
        "total_cells" => model.total_cells
    ))
end

Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

up()