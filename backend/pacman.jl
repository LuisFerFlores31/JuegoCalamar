using Agents,Agents.Pathfinding

const matrix = [
    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
]

@agent struct Ghost(GridAgent{2})
    type::String = "Ghost"
    route::Vector{Tuple{Int,Int}} = Tuple{Int,Int}[]
end

function is_valid_position(pos, model)
    col, row = pos
    filas, columnas = size(matrix)

    if row < 1 || row > filas || col < 1 || col > columnas
        return false
    end

    return matrix[row, col] == 1
end

function walk!(agent, model)
    possible_moves = [(0,-1), (0,1), (-1,0), (1,0)]
    
    current_pos = agent.pos
    valid_positions = []
    
    for direction in possible_moves
        new_pos = (
            current_pos[1] + direction[1],
            current_pos[2] + direction[2]
        )
        if is_valid_position(new_pos, model)
            push!(valid_positions, new_pos)
        end
    end
    
    if !isempty(valid_positions)
        new_pos = rand(valid_positions)
        move_agent!(agent, new_pos, model)
    end
end

function my_agent_step!(agent, model)
    if isnothing(agent.route) || isempty(agent.route)
        target = (2, 13)
        ruta_lista = plan_route!(agent, target, model.pathfinder)
        if !isnothing(ruta_lista)
            agent.route = collect(ruta_lista)
            println("Ruta creada con ", length(agent.route), " pasos")
        else
            println("No se pudo crear una ruta a $target")
            return
        end
    end
    
    old_pos = agent.pos
    move_along_route!(agent, model, model.pathfinder)
    println("Movido de $old_pos a $(agent.pos)")
end

function initialize_model()
    walkmap = BitArray(matrix .== 1)
    space = GridSpace(size(walkmap); periodic = false)
    pathfinder = AStar(space; walkmap=walkmap, diagonal_movement=false)
    properties = Dict(:pathfinder => pathfinder)
    model = StandardABM(Ghost, space;
                        properties = properties,
                        agent_step! = my_agent_step!)
    add_agent!((2, 2), model)

    return model, pathfinder
end

model, pathfinder = initialize_model()