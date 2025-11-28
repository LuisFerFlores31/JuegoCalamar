import { useState, useEffect } from 'react'

const ghostColors = {
  red: '#FF0000',
  pink: '#FFB8FF',
  cyan: '#00FFFF',
  orange: '#FFB852'
};

const App = () => {
    const [pacmans, setPacmans] = useState([]);
    const [ghosts, setGhosts] = useState([]);
    const [visitedCells, setVisitedCells] = useState([]);
    const [matrix, setMatrix] = useState([]);

    useEffect(() => {
        const interval = setInterval(() => {
            fetch("http://localhost:8000/run")
                .then(res => res.json())
                .then(res => {
                    if (res.pacmans) setPacmans(res.pacmans);
                    if (res.ghosts) setGhosts(res.ghosts);
                    if (res.visited) setVisitedCells(res.visited);
                    if (res.matrix) setMatrix(res.matrix);
                })
                .catch(error => console.error("Error al conectar con la API de Julia:", error));
        }, 1000);
        return () => clearInterval(interval);
    }, []); 

    if (matrix.length === 0) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                backgroundColor: '#1a1a1a',
                color: 'white',
                fontSize: '24px'
            }}>
                Cargando matriz...
            </div>
        );
    }

    const cellSize = Math.min(Math.floor(900 / matrix[0].length), Math.floor(900 / matrix.length));

    const isCellVisited = (col, row) => {
        return visitedCells.some(cell => cell[0] === col + 1 && cell[1] === row + 1);
    };

    const midCol = Math.floor(matrix[0].length / 2);
    const midRow = Math.floor(matrix.length / 2);

    // Posiciones de las estaciones de recarga (esquinas de cada cuadrante)
    const rechargeStations = [
        { col: 2, row: 2 },                           // Cuadrante 1 - arriba izquierda
        { col: matrix[0].length - 1, row: 2 },        // Cuadrante 2 - arriba derecha
        { col: 2, row: matrix.length - 1 },           // Cuadrante 3 - abajo izquierda
        { col: matrix[0].length - 1, row: matrix.length - 1 } // Cuadrante 4 - abajo derecha
    ];

    return (
      <div style={{
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#1a1a1a',
        overflow: 'auto'
      }}>
        <svg 
          width={cellSize * matrix[0].length} 
          height={cellSize * matrix.length} 
          xmlns="http://www.w3.org/2000/svg"
        >
          {matrix.map((row, rowidx) => 
            row.map((value, colidx) => {
              const visited = isCellVisited(colidx, rowidx);
              return (
                <rect 
                  key={`${rowidx}-${colidx}`} 
                  x={cellSize * colidx} 
                  y={cellSize * rowidx} 
                  width={cellSize} 
                  height={cellSize} 
                  fill={
                    value === 0 ? "#333" :
                    visited ? "#90EE90" :
                    "#E0E0E0"
                  }
                  stroke="#999"
                  strokeWidth="0.5"
                />
              );
            })
          )}

          {/* Estaciones de recarga (puntos morados) */}
          {rechargeStations.map((station, index) => (
            <g key={`station-${index}`}>
              <circle
                cx={cellSize * (station.col - 1) + cellSize/2}
                cy={cellSize * (station.row - 1) + cellSize/2}
                r={cellSize * 0.6}
                fill="#8B008B"
                opacity={0.8}
              />
              {/* Símbolo de rayo para indicar estación de carga */}
              <text
                x={cellSize * (station.col - 1) + cellSize/2}
                y={cellSize * (station.row - 1) + cellSize/2 + 4}
                textAnchor="middle"
                fontSize={cellSize * 0.5}
                fill="yellow"
              >
                ⚡
              </text>
            </g>
          ))}

          {/* Líneas divisorias */}
          <line 
            x1={cellSize * midCol} y1="0" 
            x2={cellSize * midCol} y2={cellSize * matrix.length} 
            stroke="black" 
            strokeWidth="4"
          />
          <line 
            x1="0" y1={cellSize * midRow} 
            x2={cellSize * matrix[0].length} y2={cellSize * midRow} 
            stroke="black" 
            strokeWidth="4"
          />

          {/* Pacmans */}
          {pacmans.map((pacman, index) => (
            <g key={`pacman-${index}`}>
              <circle
                cx={cellSize * (pacman.pos[0] - 1) + cellSize/2}
                cy={cellSize * (pacman.pos[1] - 1) + cellSize/2}
                r={cellSize * 0.4}
                fill={pacman.captured ? "#888" : "yellow"}
                opacity={pacman.captured ? 0.5 : 1}
              />
            </g>
          ))}

          {/* Fantasmas con barra de energía */}
          {ghosts.map((ghost, index) => {
            const energyPercent = ghost.energy / ghost.max_energy;
            const energyColor = energyPercent > 0.5 ? '#00FF00' : 
                               energyPercent > 0.2 ? '#FFFF00' : '#FF0000';
            
            return (
              <g key={`ghost-${index}`}>
                {/* Cuerpo del fantasma */}
                <circle
                  cx={cellSize * (ghost.pos[0] - 1) + cellSize/2}
                  cy={cellSize * (ghost.pos[1] - 1) + cellSize/2}
                  r={cellSize * 0.35}
                  fill={ghostColors[ghost.color] || '#FF0000'}
                  opacity={ghost.captured_pacman ? 0.5 : 1}
                  stroke={ghost.is_recharging ? '#FFFF00' : 'none'}
                  strokeWidth={ghost.is_recharging ? 3 : 0}
                />
                
                {/* Barra de energía (fondo) */}
                <rect
                  x={cellSize * (ghost.pos[0] - 1) + cellSize * 0.15}
                  y={cellSize * (ghost.pos[1] - 1) - cellSize * 0.2}
                  width={cellSize * 0.7}
                  height={cellSize * 0.15}
                  fill="#333"
                  rx={2}
                />
                
                {/* Barra de energía (nivel actual) */}
                <rect
                  x={cellSize * (ghost.pos[0] - 1) + cellSize * 0.15}
                  y={cellSize * (ghost.pos[1] - 1) - cellSize * 0.2}
                  width={cellSize * 0.7 * energyPercent}
                  height={cellSize * 0.15}
                  fill={energyColor}
                  rx={2}
                />
                
                {/* Indicador de recarga */}
                {ghost.is_recharging && (
                  <text
                    x={cellSize * (ghost.pos[0] - 1) + cellSize/2}
                    y={cellSize * (ghost.pos[1] - 1) - cellSize * 0.3}
                    textAnchor="middle"
                    fontSize={cellSize * 0.3}
                    fill="yellow"
                  >
                    ⚡
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    );
};

export default App;