# CMYK Splitter

A web application that converts images into CMYK color-separated halftone SVG drawings suitable for pen plotting. Upload an image and get a layered SVG with four color channels (Cyan, Magenta, Yellow, Black) that can be plotted or edited.

## Features

- **CMYK Color Separation with GCR** - Properly splits images into 4 color channels with Gray Component Replacement
- **Halftone Dot Visualization** - Converts each channel into stippled dots for clean plotting
- **Per-Channel Control** - Independent divisor settings for each color (C/M/Y default: 50, K default: 25 for finer detail)
- **Layered SVG Output** - Single SVG file with separate groups for each color channel
- **Real-Time Preview** - See all 4 colored layers overlaid with proper multiply blend mode
- **Easy Export** - Download combined SVG with all layers preserved

## Architecture

- **Backend**: FastAPI (Python) - Handles CMYK splitting with GCR and halftone dot generation
- **Frontend**: Vanilla JavaScript + dat.GUI - Interactive visualization and controls
- **Image Processing**: PIL/Pillow + NumPy for CMYK conversion with GCR, random dot sampling

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

**Debug Mode (Optional):**

To enable debug mode with verbose logging and file output:

```bash
# Set DEBUG environment variable before starting the server
DEBUG=1 uvicorn backend.main:app --reload --port 8000
```

When debug mode is enabled, the backend will:
- Print detailed processing information to console
- Save raw CMYK channel images (before thresholding) to `backend/services/debug_files/`
- Save bilevel channel images (after thresholding) to `backend/services/debug_files/`
- Save individual channel SVG files to `backend/services/debug_files/`

All debug files are timestamped (format: `YYYYMMDD_HHMMSS_*`)

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
   - Four CMYK layers will appear with colors:
     - Cyan: `rgb(0, 255, 255)`
     - Magenta: `rgb(255, 0, 255)`
     - Yellow: `rgb(255, 255, 0)`
     - Black: `rgb(0, 0, 0)`
   - All layers use multiply blend mode for proper color mixing

3. **Adjust Parameters**
   - **Divisor Sliders** - Control dot density per channel (higher = fewer dots, faster)
     - Cyan/Magenta/Yellow: 10-200 (default 50)
     - Black: 10-200 (default 25 for more detail)
   - Click "🔄 Reprocess" to regenerate with new settings

4. **Export SVG File**
   - Click "Export SVG" to download combined SVG with all 4 layers
   - Each layer is in a separate group (cyan-layer, magenta-layer, yellow-layer, black-layer)
   - SVG preserves original image dimensions

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
Process image into CMYK halftone SVG with layered output

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `image`: File (JPEG, PNG, GIF)
  - `divisor_c`: int (default 50) - Cyan dot density
  - `divisor_m`: int (default 50) - Magenta dot density
  - `divisor_y`: int (default 50) - Yellow dot density
  - `divisor_k`: int (default 25) - Black dot density
  - `skip_paths_longer_than`: int (default 25) - Unused for dot plotter

**Response (200 OK):**
```json
{
  "status": "completed",
  "result": {
    "combined_svg": "<svg width=\"1686\" height=\"2411\" xmlns=\"...\">
      <g id=\"cyan-layer\" style=\"mix-blend-mode: multiply;\">
        <circle cx=\"...\" cy=\"...\" r=\"...\" fill=\"rgb(0, 255, 255)\" />
        ...
      </g>
      <g id=\"magenta-layer\" style=\"mix-blend-mode: multiply;\">...</g>
      <g id=\"yellow-layer\" style=\"mix-blend-mode: multiply;\">...</g>
      <g id=\"black-layer\" style=\"mix-blend-mode: multiply;\">...</g>
    </svg>",
    "metadata": {
      "original_dimensions": [1686, 2411]
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
│       ├── cmyk_splitter.py    # CMYK channel splitting with GCR
│       ├── halftone_dots.py    # Halftone dot plotter
│       ├── svg_combiner.py     # Combines channel SVGs into layered output
│       └── stringy_plotter.py  # Continuous line path generation (alternative)
├── lib/                        # Frontend libraries (dat.GUI)
├── api-client.js               # Frontend API communication
├── cmyk-controls.js            # dat.GUI controls
├── index.html                  # Main HTML page
├── sketch.js                   # CMYK visualization
├── style.css                   # Styling
├── svgtools.js                 # SVG export utilities
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Algorithm Details

### CMYK Splitting with GCR
1. Convert RGB to CMY: `C = 1-R, M = 1-G, Y = 1-B`
2. Calculate K (gray component): `K = min(C, M, Y)`
3. Extract gray from CMY (Gray Component Replacement):
   - `C = (C - K) / (1 - K)`
   - `M = (M - K) / (1 - K)`
   - `Y = (Y - K) / (1 - K)`
4. Apply thresholds to create bilevel (black/white) images:
   - Cyan: 50% threshold (127/255)
   - Magenta: 50% threshold (127/255)
   - Yellow: 65% threshold (165/255) - yellows need special handling
   - Black: 50% threshold (127/255)

### Halftone Dot Plotter
1. Extract white pixels (ink areas) from bilevel image
2. Randomly sample pixels up to max_dots (default 2000)
3. Place SVG circles at sampled positions
4. Combine all channel SVGs into single layered output with:
   - Separate groups for each color
   - Proper RGB colors applied
   - Multiply blend mode for color mixing

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
- Increase divisor values (fewer dots = faster processing)
- HalftoneDotPlotter has a hard cap of 2000 dots per channel by default
- Black channel typically needs lower divisor (more detail) than other channels

## Development Notes

- Backend uses **FastAPI** with async/await for potential future enhancements
- Frontend is purely static - no build step required
- CORS enabled for `localhost:8080` - update `backend/main.py` for other ports
- GCR (Gray Component Replacement) implemented in pure Python using NumPy
- Debug mode can be enabled with `DEBUG=1` environment variable - see "Running the Application" section

## Credits

- Built with [FastAPI](https://fastapi.tiangolo.com/), [Pillow](https://python-pillow.org/), and [NumPy](https://numpy.org/)
- dat.GUI for controls

## License

See individual components for their respective licenses.
