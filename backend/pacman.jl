using Agents
using Agents.Pathfinding
using Random
using DelimitedFiles

function load_matrix_from_csv(filepath::String)
    if !isfile(filepath)
        for f in readdir()
            if endswith(lowercase(f), ".csv")
            end
        end
        error("Archivo no encontrado")
    end
    matrix = readdlm(filepath, ',', Int)
    println("✅ Matriz cargada: $(size(matrix)[1])x$(size(matrix)[2])")
    return matrix
end

const matrix_path = joinpath(@__DIR__, "Matriz.csv")

const matrix = load_matrix_from_csv(matrix_path)

@agent struct Pacman(GridAgent{2})
    type::String = "Pacman"
    color::String = "yellow"
    quadrant::Int = 1
    captured::Bool = false
end

@agent struct Ghost(GridAgent{2})
    type::String = "Ghost"
    color::String = "red"
    quadrant::Int = 1
    target_id::Int = 1
    captured_pacman::Bool = false
    patrol_direction::String = "right"
    vision_range::Int = 10
    chasing::Bool = false
end

function get_quadrant_bounds(quadrant, matrix_size)
    rows, cols = matrix_size
    mid_row = div(rows + 1, 2)
    mid_col = div(cols + 1, 2)
    
    if quadrant == 1
        return (col_min=1, col_max=mid_col-1, row_min=1, row_max=mid_row-1)
    elseif quadrant == 2
        return (col_min=mid_col+1, col_max=cols, row_min=1, row_max=mid_row-1)
    elseif quadrant == 3
        return (col_min=1, col_max=mid_col-1, row_min=mid_row+1, row_max=rows)
    else
        return (col_min=mid_col+1, col_max=cols, row_min=mid_row+1, row_max=rows)
    end
end

function is_divisor(pos, matrix_size)
    col, row = pos
    rows, cols = matrix_size
    mid_row = div(rows + 1, 2)
    mid_col = div(cols + 1, 2)
    return col == mid_col || row == mid_row
end

function pacman_step!(agent, model)
    if agent.captured
        return
    end
    
    possible_moves = [
        (agent.pos[1], agent.pos[2] - 1),
        (agent.pos[1], agent.pos[2] + 1),
        (agent.pos[1] - 1, agent.pos[2]),
        (agent.pos[1] + 1, agent.pos[2])
    ]
    
    valid_moves = []
    filas, columnas = size(matrix)
    
    for new_pos in possible_moves
        col, row = new_pos
        if row >= 1 && row <= filas && col >= 1 && col <= columnas
            if matrix[row, col] == 1 || is_divisor(new_pos, (filas, columnas))
                push!(valid_moves, new_pos)
            end
        end
    end
    
    if !isempty(valid_moves)
        new_pos = rand(valid_moves)
        push!(model.visited_cells, new_pos)
        move_agent!(agent, new_pos, model)
    end
end

function distance(pos1, pos2)
    return abs(pos1[1] - pos2[1]) + abs(pos1[2] - pos2[2])
end

function patrol_zigzag!(agent, model)
    matrix_size = size(matrix)
    bounds = get_quadrant_bounds(agent.quadrant, matrix_size)
    new_pos = agent.pos

    if agent.patrol_direction == "right"
        new_pos = (agent.pos[1] + 1, agent.pos[2])
        if new_pos[1] > bounds.col_max || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "down"
        end
    elseif agent.patrol_direction == "down"
        new_pos = (agent.pos[1], agent.pos[2] + 1)
        if new_pos[2] > bounds.row_max || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "left"
        end
    elseif agent.patrol_direction == "left"
        new_pos = (agent.pos[1] - 1, agent.pos[2])
        if new_pos[1] < bounds.col_min || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "up"
        end
    elseif agent.patrol_direction == "up"
        new_pos = (agent.pos[1], agent.pos[2] - 1)
        if new_pos[2] < bounds.row_min || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "right"
        end
    end

    col, row = new_pos
    if bounds.col_min <= col <= bounds.col_max && bounds.row_min <= row <= bounds.row_max && matrix[row, col] == 1
        move_agent!(agent, new_pos, model)
    end
end

function ghost_step!(agent, model)
    if agent.captured_pacman
        return
    end
    patrol_zigzag!(agent, model) 
end


function initialize_model()
    walkmap = BitArray(matrix .== 1)
    space = GridSpace(size(walkmap); periodic = false)
    pathfinder = AStar(space; walkmap=walkmap, diagonal_movement=false)
    
    properties = Dict(
        :pathfinder => pathfinder,
        :visited_cells => Set{Tuple{Int,Int}}()
    )
    
    model = StandardABM(Union{Pacman, Ghost}, space;
                        properties = properties,
                        agent_step! = agent_step!,
                        warn=false)
    
    rows, cols = size(matrix)
    mid_row = div(rows + 1, 2)
    mid_col = div(cols + 1, 2)
    
    println("Tamaño de matriz: $(rows)x$(cols) | Divisor fila: $(mid_row) columna: $(mid_col)")
    
    # ==== PACMANS ====
    pacman_positions = [
        (2, 2),
        (cols - 1, 2),
        (2, rows - 1),
        (cols - 1, rows - 1)
    ]
    
    for pos in pacman_positions
        add_agent!(pos, Pacman, model)
    end
    
    # ==== GHOSTS ====
    ghost_positions = [
        (mid_col, 2),            
        (mid_col, rows - 1),     
        (2, mid_row),            
        (cols - 1, mid_row)      
    ]
    
    for (i, pos) in enumerate(ghost_positions)
        g = add_agent!(pos, Ghost, model)
        g.quadrant = i
    end

    return model
end


function agent_step!(agent, model)
    if agent isa Pacman
        pacman_step!(agent, model)
    elseif agent isa Ghost
        ghost_step!(agent, model)
    end
end

# Crear modelo global
model = initialize_model()
