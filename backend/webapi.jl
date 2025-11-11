include("pacman.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

route("/run") do
    if !model.running
        return json(Dict("error" => "Simulación finalizada"))
    end
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

    # DEBUG: Imprimir información de celdas
    println("========== DEBUG ==========")
    println("Celdas pintadas: $(model.painted_cells)")
    println("Total de celdas: $(model.total_cells)")
    println("Porcentaje pintado: $(round(model.painted_cells / model.total_cells * 100, digits=2))%")
    println("Calamares ganaron: $(model.squids_won)")
    println("Fantasmas ganaron: $(model.ghosts_won)")
    println("===========================")

    if model.squids_won || model.ghosts_won
        model.running = false
    end

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