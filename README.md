# CMYK Splitter

A web application that converts images into CMYK color-separated "stringy" SVG drawings suitable for pen plotting. Upload an image and get four continuous-line SVG layers (Cyan, Magenta, Yellow, Black) that can be plotted individually or combined.

## Features

- **CMYK Color Separation** - Automatically splits images into 4 color channels
- **Continuous Line Algorithm** - Converts each channel into a single continuous path using nearest-neighbor traversal
- **Per-Channel Control** - Independent divisor settings for each color (C/M/Y default: 50, K default: 25 for finer detail)
- **Layer Visibility** - Toggle each CMYK layer on/off in real-time preview
- **Multiple Export Options** - Export individual channels or combined SVG
- **Real-Time Preview** - See all 4 colored layers overlaid with proper transparency

## Architecture

- **Backend**: FastAPI (Python) - Handles CMYK splitting and stringy path generation
- **Frontend**: p5.js + dat.GUI - Interactive visualization and controls
- **Image Processing**: PIL/Pillow for CMYK conversion, SciPy for nearest-neighbor path finding

## Setup

### Requirements

- Python 3.12 (recommended) or Python 3.11
- Modern web browser

### 1. Backend Setup

```bash
cd cmyk-splitter/

# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

No additional setup required - the frontend is a static HTML/JS application.

## Running the Application

You'll need two terminal windows running simultaneously.

### Terminal 1: Start Backend Server

```bash
cd cmyk-splitter/

# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn backend.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2: Start Frontend Server

```bash
cd cmyk-splitter/

# Start simple HTTP server
python3 -m http.server 8080
```

The frontend will be available at `http://localhost:8080`

### 3. Open in Browser

Navigate to `http://localhost:8080` in your web browser.

## Usage

1. **Upload Image**
   - Click "📁 Select Image" in the dat.GUI controls (top right)
   - Choose an image file (JPEG, PNG, GIF)
   - Wait for processing (status shown in top-left panel)

2. **View Results**
   - Four CMYK layers will appear on canvas with colors:
     - Cyan: `#00FFFF` (light blue, semi-transparent)
     - Magenta: `#FF00FF` (purple-pink, semi-transparent)
     - Yellow: `#FFFF00` (yellow, semi-transparent)
     - Black: `#000000` (black, opaque)

3. **Adjust Parameters**
   - **Divisor Sliders** - Control point density per channel (higher = fewer points, faster)
     - Cyan/Magenta/Yellow: 10-200 (default 50)
     - Black: 10-200 (default 25 for more detail)
   - **Skip Paths >** - Max distance for continuous lines (5-100, default 25)
   - Click "🔄 Reprocess" to regenerate with new settings

4. **Toggle Layer Visibility**
   - Use checkboxes to show/hide individual channels
   - Useful for inspecting individual color separations

5. **Export SVG Files**
   - **Export Cyan/Magenta/Yellow/Black** - Download individual channel as SVG
   - **Export Combined** - Download all 4 layers in one SVG file

## API Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /api/process-image`
Process image into CMYK stringy SVG layers

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `image`: File (JPEG, PNG, GIF)
  - `divisor_c`: int (default 50)
  - `divisor_m`: int (default 50)
  - `divisor_y`: int (default 50)
  - `divisor_k`: int (default 25)
  - `skip_paths_longer_than`: int (default 25)

**Response (200 OK):**
```json
{
  "status": "completed",
  "result": {
    "cyan_svg": "<svg width=\"800\" height=\"600\">...</svg>",
    "magenta_svg": "<svg width=\"800\" height=\"600\">...</svg>",
    "yellow_svg": "<svg width=\"800\" height=\"600\">...</svg>",
    "black_svg": "<svg width=\"800\" height=\"600\">...</svg>",
    "metadata": {
      "original_dimensions": [800, 600]
    }
  }
}
```

## Project Structure

```
cmyk-splitter/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   └── routes.py           # API endpoints
│   └── services/
│       ├── cmyk_splitter.py    # CMYK channel splitting
│       └── stringy_plotter.py  # Continuous line path generation
├── flowers/                     # Original Python CLI script (reference)
├── lib/                        # Frontend libraries (p5.js, dat.GUI, paper.js)
├── api-client.js               # Frontend API communication
├── cmyk-controls.js            # dat.GUI controls
├── index.html                  # Main HTML page
├── sketch.js                   # p5.js sketch & CMYK visualization
├── style.css                   # Styling
├── svgtools.js                 # SVG export utilities
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Algorithm Details

### CMYK Splitting
1. Convert RGB image to CMYK color space using PIL
2. Split into 4 separate channels (C, M, Y, K)
3. Apply thresholds to create bilevel (black/white) images:
   - Cyan, Magenta, Black: 50% threshold (127/255)
   - Yellow: 65% threshold (165/255) - yellows need special handling

### Stringy Plotter
1. Extract all black pixels from bilevel image
2. Randomly sample pixels based on divisor (e.g., every 50th pixel)
3. Connect sampled points using **greedy nearest-neighbor traversal**:
   - Start with first point
   - Find closest unvisited point
   - Connect and repeat
4. Generate SVG path with M (move) and L (line) commands:
   - Use L (line) for distances ≤ threshold
   - Use M (move) for distances > threshold (lifts pen, breaks line)

## Troubleshooting

### Backend won't start
- Make sure virtual environment is activated: `source venv/bin/activate`
- Check Python version: `python --version` (should be 3.12 or 3.11)
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend shows "Backend not available"
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Try accessing `http://localhost:8000/health` directly

### Processing is slow
- Increase divisor values (fewer points = faster processing)
- Use smaller images (StringyPlotter is O(n²) with number of points)
- Black channel typically needs lower divisor (more detail) than other channels

### Python 3.14 installation errors
- Use Python 3.12 or 3.11 instead (pre-built wheels available)
- NumPy and Pillow don't have wheels for Python 3.14 yet

## Development Notes

- Backend uses **FastAPI** with async/await for potential future enhancements
- Frontend is purely static - no build step required
- CORS enabled for `localhost:8080` - update `backend/main.py` for other ports
- Spiral demo code kept in `sketch.js` as fallback (shows when no image uploaded)

## Credits

- Original StringyPlotter algorithm by [th0ma5w](https://github.com/th0ma5w/StringyPlotter)
- Built with [p5.js](https://p5js.org/), [FastAPI](https://fastapi.tiangolo.com/), and [Pillow](https://python-pillow.org/)

## License

See individual components for their respective licenses.
