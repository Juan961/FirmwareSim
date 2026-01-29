import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os


FILENAME = 'debug_grid.txt'
PATH_FILENAME = 'debug_path.txt'
GRID_SIZE = 120


def load_grid(filename):
    try:
        if not os.path.exists(filename):
            return None

        with open(filename, 'r') as f:
            lines = f.readlines()
            # Parse each line into a list of floats
            grid = []
            for line in lines:
                try:
                    row = [float(x) for x in line.strip().split()]
                    if len(row) > 0:
                        grid.append(row)
                except ValueError:
                    continue
            
            if not grid:
                return None
                
            return np.array(grid)
            
    except Exception as e:
        print(f"Error reading grid: {e}")
        return None


def load_path(filename):
    try:
        if not os.path.exists(filename):
            return []

        with open(filename, 'r') as f:
            lines = f.readlines()
            path = []
            for line in lines:
                try:
                    x, y = map(int, line.strip().split())
                    path.append((x, y))
                except ValueError:
                    continue
            
            return path
            
    except Exception as e:
        print(f"Error reading path: {e}")
        return []


def update_plot(frame, img, ax, path_line):
    grid = load_grid(FILENAME)

    if grid is not None:
        masked_grid = np.ma.masked_equal(grid, -1.0)
        img.set_data(masked_grid)
        
        # Load and display the path from file
        path = load_path(PATH_FILENAME)
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            path_line.set_data(path_x, path_y)
        else:
            path_line.set_data([], [])
        
        return [img, path_line]
    else:
        print("Waiting for grid file...")
        return [img, path_line]


def main():
    print(f"Monitoring {FILENAME}...")
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    initial_data = np.zeros((GRID_SIZE, GRID_SIZE))

    cmap = plt.get_cmap('Greys').copy()
    cmap.set_bad(color='red')
    
    img = ax.imshow(initial_data, cmap=cmap, vmin=0, vmax=1, origin='lower')
    
    path_line, = ax.plot([], [], 'g-', linewidth=2, label='Path')
    ax.legend()
    
    ax.set_title(f"Robot Occupancy Grid ({GRID_SIZE}x{GRID_SIZE})")
    ax.set_xlabel("X Index")
    ax.set_ylabel("Y Index")
    
    ax.grid(which='major', axis='both', linestyle='-', color='blue', linewidth=0.5, alpha=0.3)
    
    ani = animation.FuncAnimation(fig, update_plot, fargs=(img, ax, path_line), interval=1000, blit=True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
