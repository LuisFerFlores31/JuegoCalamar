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

          {/* líneas divisorias */}
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

          {/* Fantasmas */}
          {ghosts.map((ghost, index) => (
            <g key={`ghost-${index}`}>
              <circle
                cx={cellSize * (ghost.pos[0] - 1) + cellSize/2}
                cy={cellSize * (ghost.pos[1] - 1) + cellSize/2}
                r={cellSize * 0.35}
                fill={ghostColors[ghost.color] || '#FF0000'}
                opacity={ghost.captured_pacman ? 0.5 : 1}
              />
            </g>
          ))}
        </svg>
      </div>
    );
};

export default App;
