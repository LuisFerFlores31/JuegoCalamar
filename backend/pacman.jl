using Agents
using Agents.Pathfinding
using Random
using DelimitedFiles

#Cargar matriz en el archivo csv Matriz.csv
function load_matrix_from_csv(filepath::String)
    if !isfile(filepath)
        error("Falla del archivo")
    end
    matrix = readdlm(filepath, ',', Int)
    return matrix
end

const matrix_path = joinpath(@__DIR__, "Matriz.csv")
const matrix = load_matrix_from_csv(matrix_path)

# Los agentes pacman y ghost
@agent struct Pacman(GridAgent{2})
    type::String = "Pacman"
    color::String = "yellow"
    quadrant::Int = 1
    captured::Bool = false
    is_escaping::Bool = false
    escape_steps::Int = 0
    tired_steps::Int = 0
    last_direction::Tuple{Int,Int} = (1, 0)  # Última dirección de movimiento
    target_cell::Union{Tuple{Int,Int}, Nothing} = nothing  # Objetivo persistente
end

@agent struct Ghost(GridAgent{2})
    type::String = "Ghost"
    color::String = "red"
    quadrant::Int = 1
    target_id::Union{Int,Nothing} = nothing
    captured_pacman::Bool = false
    patrol_direction::String = "right"
    vision_range::Int = 8 #Campo de Vision (aumentado de 5 a 8)
    chasing::Bool = false
    # Sistema de energía
    energy::Int = 100           # Energía actual
    max_energy::Int = 100       # Energía máxima
    energy_threshold::Int = 20  # Umbral para ir a recargar
    is_recharging::Bool = false # Estado de recarga
    recharge_rate::Int = 10     # Cuánta energía recupera por paso en la estación
end

# Posiciones de las estaciones de recarga (puntos morados en las esquinas de cada cuadrante)
function get_recharge_station(quadrant::Int, matrix_size)
    rows, cols = matrix_size
    mid_row = div(rows + 1, 2)
    mid_col = div(cols + 1, 2)
    
    if quadrant == 1      # Arriba izquierda -> esquina superior izquierda
        return (2, 2)
    elseif quadrant == 2  # Arriba derecha -> esquina superior derecha
        return (cols - 1, 2)
    elseif quadrant == 3  # Abajo izquierda -> esquina inferior izquierda
        return (2, rows - 1)
    else                  # Abajo derecha -> esquina inferior derecha
        return (cols - 1, rows - 1)
    end
end

#Division de cuadrantes
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

function distance(pos1, pos2)
    return abs(pos1[1] - pos2[1]) + abs(pos1[2] - pos2[2])
end

# Función para encontrar la celda blanca 
function find_nearest_unvisited(pos, model)
    filas, columnas = size(matrix)
    nearest = nothing
    min_dist = Inf
    
    for col in 1:columnas
        for row in 1:filas
            cell = (col, row)
            # Solo considerar celdas caminables y no visitadas
            if matrix[row, col] == 1 && !(cell in model.visited_cells)
                dist = distance(pos, cell)
                if dist < min_dist
                    min_dist = dist
                    nearest = cell
                end
            end
        end
    end
    
    return nearest
end

# Función para elegir el mejor movimiento hacia un objetivo
function move_towards(pos, target, valid_moves)
    if isnothing(target) || isempty(valid_moves)
        return nothing
    end
    
    best_move = nothing
    min_dist = Inf
    
    for move in valid_moves
        dist = distance(move, target)
        if dist < min_dist
            min_dist = dist
            best_move = move
        end
    end
    
    return best_move
end

# Función para pintar 5 celdas: 1 atrás, 1 a cada lado, y las 2 esquinas traseras
function paint_brush_pattern!(pos, direction, model)
    filas, columnas = size(matrix)
    dx, dy = direction
    
    # Calcular direcciones según el movimiento
    if dx != 0  # Movimiento horizontal 
        back_dx, back_dy = -dx, 0      
        perp_dx, perp_dy = 0, 1        
    else        # Movimiento vertical (arriba/abajo)
        back_dx, back_dy = 0, -dy      
        perp_dx, perp_dy = 1, 0       
    end
    
    # Las 5 celdas a pintar (no incluye la celda actual, esa se maneja aparte)
    cells_to_paint = [
        (pos[1] + back_dx, pos[2] + back_dy),                           
        (pos[1] + perp_dx, pos[2] + perp_dy),                           
        (pos[1] - perp_dx, pos[2] - perp_dy),                           
        (pos[1] + back_dx + perp_dx, pos[2] + back_dy + perp_dy),       
        (pos[1] + back_dx - perp_dx, pos[2] + back_dy - perp_dy)        
    ]
    
    # Pintar celdas válidas
    for cell in cells_to_paint
        col, row = cell
        if row >= 1 && row <= filas && col >= 1 && col <= columnas
            if matrix[row, col] == 1 && !(cell in model.visited_cells)
                push!(model.visited_cells, cell)
                model.painted_cells += 1
            end
        end
    end
end

function pacman_step!(agent, model)
    if agent.captured
        return
    end
    
    # Detectar si hay fantasmas cerca
    escaping = false
    threat_direction = nothing
    
    for other in allagents(model)
        if other isa Ghost && other.chasing && !isnothing(other.target_id) && other.target_id == agent.id
            dist = distance(agent.pos, other.pos)
            if dist <= 8 #Zona de escape amplia
                escaping = true
                #Calcular dirección de la amenaza
                threat_direction = (other.pos[1] - agent.pos[1], other.pos[2] - agent.pos[2])
                break
            end
        end
    end
    
    # Actualizar estado de escape
    if escaping
        if !agent.is_escaping
            agent.is_escaping = true
            agent.escape_steps = 0
            agent.tired_steps = 0
        end
    else
        agent.is_escaping = false
        agent.escape_steps = 0
        agent.tired_steps = 0
    end
    
    # Si está cansado, no se mueve
    if agent.is_escaping && agent.tired_steps > 0
        agent.tired_steps -= 1
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
    
    if isempty(valid_moves)
        return
    end
    
    chosen_move = nothing
    # Escapar del fantasma
    if escaping && !isnothing(threat_direction)
        best_move = nothing
        max_distance = -Inf
        # Tratar de escapar lo más lejos posible
        for move in valid_moves
            move_away_score = -(threat_direction[1] * (move[1] - agent.pos[1]) + 
                               threat_direction[2] * (move[2] - agent.pos[2]))
            
            if move_away_score > max_distance
                max_distance = move_away_score
                best_move = move
            end
        end
        chosen_move = best_move
        agent.target_cell = nothing  # Resetear objetivo al escapar
    else
        #Buscar celdas no pintadas entre los vecinos
        unvisited = [m for m in valid_moves if !(m in model.visited_cells)]
        
        if !isempty(unvisited)
            # Si hay vecinos no visitados, elegir uno al azar y resetear objetivo
            chosen_move = rand(unvisited)
            agent.target_cell = nothing
        else
            # Si no hay vecinos no visitados, usar objetivo persistente
            
            # Verificar si el objetivo actual sigue siendo válido
            if !isnothing(agent.target_cell)
                if agent.target_cell in model.visited_cells || agent.pos == agent.target_cell
                    agent.target_cell = nothing  # Ya fue visitado o llegamos
                end
            end
            
            # Si no hay objetivo, buscar uno nuevo
            if isnothing(agent.target_cell)
                agent.target_cell = find_nearest_unvisited(agent.pos, model)
            end
            
            # Moverse hacia el objetivo
            if !isnothing(agent.target_cell)
                chosen_move = move_towards(agent.pos, agent.target_cell, valid_moves)
            else
                # Si ya no hay celdas blancas, moverse al azar
                chosen_move = rand(valid_moves)
            end
        end
    end
    
    if !isnothing(chosen_move)
        # Calcular la dirección del movimiento
        move_direction = (chosen_move[1] - agent.pos[1], chosen_move[2] - agent.pos[2])
        agent.last_direction = move_direction
        
        move_agent!(agent, chosen_move, model)
        
        # Marcar la celda actual como visitada 
        if !(agent.pos in model.visited_cells)
            push!(model.visited_cells, agent.pos)
            # Solo contar si es celda caminable 
            filas, columnas = size(matrix)
            if matrix[agent.pos[2], agent.pos[1]] == 1
                model.painted_cells += 1
            end
        end
        
        # Pintar las 5 celdas adicionales en patrón de brocha
        paint_brush_pattern!(agent.pos, move_direction, model)
        
        # Verificar victoria cuando se pinta una nueva celda
        if model.painted_cells >= model.total_cells
            model.squids_won = true
            println("¡Los calamares han ganado! Pintaron $(model.painted_cells) de $(model.total_cells) celdas")
        end
        
        # Incrementar contador de pasos si está escapando
        if agent.is_escaping
            agent.escape_steps += 1
            # Si completó 5 pasos, se cansa por 2 pasos
            if agent.escape_steps >= 5
                agent.tired_steps = 2
                agent.escape_steps = 0
                println("¡Pacman $(agent.id) se cansó! Descansando por 2 pasos...")
            end
        end
    end
end

#Esta funcion es unicamente del fantasma, que va a hacer un camino cuando no este persiguiendo a un pacman
function patrol_zigzag!(agent, model)
    matrix_size = size(matrix)
    bounds = get_quadrant_bounds(agent.quadrant, matrix_size)
    new_pos = agent.pos

    if agent.patrol_direction == "right"
        new_pos = (agent.pos[1] + 1, agent.pos[2])
        if new_pos[1] > bounds.col_max || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "down"
            new_pos = (agent.pos[1], agent.pos[2] + 1)
        end
    elseif agent.patrol_direction == "down"
        new_pos = (agent.pos[1], agent.pos[2] + 1)
        if new_pos[2] > bounds.row_max || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "left"
            new_pos = (agent.pos[1] - 1, agent.pos[2])
        end
    elseif agent.patrol_direction == "left"
        new_pos = (agent.pos[1] - 1, agent.pos[2])
        if new_pos[1] < bounds.col_min || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "up"
            new_pos = (agent.pos[1], agent.pos[2] - 1)
        end
    elseif agent.patrol_direction == "up"
        new_pos = (agent.pos[1], agent.pos[2] - 1)
        if new_pos[2] < bounds.row_min || matrix[new_pos[2], new_pos[1]] == 0
            agent.patrol_direction = "right"
            new_pos = (agent.pos[1] + 1, agent.pos[2])
        end
    end

    col, row = new_pos
    if bounds.col_min <= col <= bounds.col_max && 
       bounds.row_min <= row <= bounds.row_max && 
       matrix[row, col] == 1
        move_agent!(agent, new_pos, model)
    end
end

#Funcion para el fantasma que persigue al pacman
function chase_pacman!(agent, target_pacman, model)
    if isnothing(target_pacman) || target_pacman.captured
        return
    end
    
    dx = target_pacman.pos[1] - agent.pos[1]
    dy = target_pacman.pos[2] - agent.pos[2]
    
    moves = []
    if abs(dx) >= abs(dy)
        dx > 0 ? push!(moves, (agent.pos[1] + 1, agent.pos[2])) : push!(moves, (agent.pos[1] - 1, agent.pos[2]))
        dy > 0 ? push!(moves, (agent.pos[1], agent.pos[2] + 1)) : dy < 0 && push!(moves, (agent.pos[1], agent.pos[2] - 1))
    else
        dy > 0 ? push!(moves, (agent.pos[1], agent.pos[2] + 1)) : push!(moves, (agent.pos[1], agent.pos[2] - 1))
        dx > 0 ? push!(moves, (agent.pos[1] + 1, agent.pos[2])) : dx < 0 && push!(moves, (agent.pos[1] - 1, agent.pos[2]))
    end
    
    matrix_size = size(matrix)
    bounds = get_quadrant_bounds(agent.quadrant, matrix_size)
    
    for new_pos in moves
        col, row = new_pos
        if bounds.col_min <= col <= bounds.col_max && 
           bounds.row_min <= row <= bounds.row_max &&
           matrix[row, col] == 1
            move_agent!(agent, new_pos, model)
            
            if agent.pos == target_pacman.pos
                println("Fantasma $(agent.color) atrapó a Pacman $(target_pacman.id)")
                agent.captured_pacman = true
                target_pacman.captured = true
                
                # Verificar si todos los pacmans fueron capturados
                all_captured = all(p.captured for p in allagents(model) if p isa Pacman)
                if all_captured
                    model.ghosts_won = true
                    println("¡Los fantasmas han ganado! Capturaron a todos los calamares")
                end
            end
            return
        end
    end
end

# Función para mover el fantasma hacia la estación de recarga
function move_to_recharge_station!(agent, model)
    matrix_size = size(matrix)
    bounds = get_quadrant_bounds(agent.quadrant, matrix_size)
    station_pos = get_recharge_station(agent.quadrant, matrix_size)
    
    # Si ya está en la estación, recargar
    if agent.pos == station_pos
        agent.energy = min(agent.energy + agent.recharge_rate, agent.max_energy)
        println("Fantasma $(agent.color) recargando... Energía: $(agent.energy)/$(agent.max_energy)")
        
        # Si llegó a energía máxima, dejar de recargar
        if agent.energy >= agent.max_energy
            agent.is_recharging = false
            println("Fantasma $(agent.color) completó la recarga!")
        end
        return
    end
    
    # Calcular dirección hacia la estación
    dx = station_pos[1] - agent.pos[1]
    dy = station_pos[2] - agent.pos[2]
    
    moves = []
    # Priorizar el eje con mayor distancia
    if abs(dx) >= abs(dy)
        dx > 0 ? push!(moves, (agent.pos[1] + 1, agent.pos[2])) : push!(moves, (agent.pos[1] - 1, agent.pos[2]))
        dy > 0 ? push!(moves, (agent.pos[1], agent.pos[2] + 1)) : dy < 0 && push!(moves, (agent.pos[1], agent.pos[2] - 1))
    else
        dy > 0 ? push!(moves, (agent.pos[1], agent.pos[2] + 1)) : push!(moves, (agent.pos[1], agent.pos[2] - 1))
        dx > 0 ? push!(moves, (agent.pos[1] + 1, agent.pos[2])) : dx < 0 && push!(moves, (agent.pos[1] - 1, agent.pos[2]))
    end
    
    # Intentar moverse hacia la estación
    for new_pos in moves
        col, row = new_pos
        if bounds.col_min <= col <= bounds.col_max && 
           bounds.row_min <= row <= bounds.row_max &&
           matrix[row, col] == 1
            move_agent!(agent, new_pos, model)
            return
        end
    end
end

function ghost_step!(agent, model)
    if agent.captured_pacman
        return
    end
    
    matrix_size = size(matrix)
    bounds = get_quadrant_bounds(agent.quadrant, matrix_size)
    station_pos = get_recharge_station(agent.quadrant, matrix_size)
    
    # Verificar si necesita ir a recargar (prioridad máxima)
    if agent.energy <= agent.energy_threshold && !agent.is_recharging
        agent.is_recharging = true
        agent.chasing = false
        agent.target_id = nothing
        println("⚡ Fantasma $(agent.color) tiene poca energía ($(agent.energy))! Yendo a recargar...")
    end
    
    # Si está en modo recarga, ir a la estación
    if agent.is_recharging
        move_to_recharge_station!(agent, model)
        # No consumir energía mientras recarga (ya está en la estación o yendo hacia ella)
        if agent.pos != station_pos
            agent.energy -= 1  # Consumir energía solo mientras se mueve hacia la estación
        end
        return
    end
    
    # Consumir energía en cada paso (solo si no está recargando)
    agent.energy -= 2
    
    # Buscar Pacmans en FOV dentro del cuadrante
    closest_pacman = nothing
    min_distance = Inf
    
    for other_agent in allagents(model)
        if other_agent isa Pacman && !other_agent.captured
            # Verificar si está el cuadrante 
            in_quadrant = (bounds.col_min <= other_agent.pos[1] <= bounds.col_max &&
                          bounds.row_min <= other_agent.pos[2] <= bounds.row_max &&
                          !is_divisor(other_agent.pos, matrix_size))
            
            if in_quadrant
                dist = distance(agent.pos, other_agent.pos)
                # Si esta dentro del FOV campo de vision we y es el más cercano
                if dist <= agent.vision_range && dist < min_distance
                    min_distance = dist
                    closest_pacman = other_agent
                end
            end
        end
    end
    
    # Si se detecto un Pacman, perseguirlo
    if !isnothing(closest_pacman)
        if !agent.chasing
            println("Fantasma $(agent.color) detectó a Pacman $(closest_pacman.id) a distancia $(min_distance)!")
        end
        agent.chasing = true
        agent.target_id = closest_pacman.id
        chase_pacman!(agent, closest_pacman, model)
    else
        # No hay Pacmans en FOV o salió del cuadrante
        if agent.chasing
            println("Fantasma $(agent.color) dejó de seguir a Pacman.")
        end
        agent.chasing = false
        agent.target_id = nothing
        patrol_zigzag!(agent, model)
    end
end

# Pasos de los agentes
function agent_step!(agent, model)
    if agent isa Pacman
        pacman_step!(agent, model)
    else
        ghost_step!(agent, model)
    end
end

# Aqui se inicia el modelo, abajo puedes cambiar cuantos pacman y fantasmas quieres
function initialize_model()
    walkmap = BitArray(matrix .== 1)
    space = GridSpace(size(walkmap); periodic = false)
    pathfinder = AStar(space; walkmap=walkmap, diagonal_movement=false)
    
    properties = Dict(
        :pathfinder => pathfinder,
        :visited_cells => Set{Tuple{Int,Int}}(),
        :total_cells => sum(matrix .== 1),
        :painted_cells => 0,
        :squids_won => false,
        :ghosts_won => false,
        :running => true
    )
    
    model = StandardABM(Union{Pacman, Ghost}, space;
                        properties = properties,
                        agent_step! = agent_step!,
                        warn=false)
    
    rows, cols = size(matrix)
    mid_row = div(rows + 1, 2)
    mid_col = div(cols + 1, 2)
    
    # Pacmans
    pacman_positions = [(10, 10), (31, 10), (10, 31), (31, 31)]
    #pacman_positions = [(2, 3)]
    for (i, pos) in enumerate(pacman_positions)
        p = add_agent!(pos, Pacman, model)
        p.quadrant = i
        p.last_direction = (1, 0)  # Dirección inicial: derecha
        p.target_cell = nothing    # Sin objetivo inicial
    end
    
    # Fantasmas (inician en las estaciones de recarga)
    ghost_positions = [(2, 2), (40, 2), (2, 40), (40, 40)]
    #ghost_positions = [(2,2)]
    ghost_colors = ["red", "orange", "pink", "cyan"]
    
    for (i, pos) in enumerate(ghost_positions)
        g = add_agent!(pos, Ghost, model)
        g.quadrant = i
        g.color = ghost_colors[i]
        # Configurar energía inicial
        g.energy = 100
        g.max_energy = 100
        g.energy_threshold = 20
        g.is_recharging = false
        g.recharge_rate = 10
    end
    
    return model
end

model = initialize_model()