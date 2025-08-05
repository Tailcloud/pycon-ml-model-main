# Flight Delay Prediction Dashboard

This dashboard provides a visual interface for the flight delay prediction ML model, allowing users to interactively predict flight delays based on airport and day of week.

## Features

### Visual Dashboard
- **Interactive Form**: Select airport and day of week for predictions
- **Real-time Predictions**: Get instant ML-powered predictions
- **Visual Charts**: Beautiful donut chart showing prediction probabilities
- **Live Statistics**: Track total predictions, average delay probability, and most queried airport

### Prediction Display
- **On-Time Probability**: Large percentage display in green
- **Delay Probability**: Large percentage display in red  
- **Visual Chart**: CSS-based donut chart with legend
- **Summary Stats**: Running statistics of usage patterns

## Usage

### Running the Dashboard

```bash
cd server
python simple_server.py
```

The dashboard will be available at `http://localhost:8000`

### Making Predictions

1. **Select Airport**: Choose from 70+ available airports
2. **Select Day**: Pick Monday through Sunday
3. **Click Predict**: Get instant ML predictions
4. **View Results**: See probabilities and visual chart

### API Endpoints

- `GET /` - Main dashboard interface
- `GET /predict?airport_id=X&day_of_week=Y` - Get prediction JSON
- `GET /airports` - List all available airports
- `GET /api/stats` - Get usage statistics

## Technical Details

### Architecture
- **Backend**: Python HTTP server (no external dependencies)
- **Frontend**: HTML/CSS/JavaScript (no external CDNs)
- **Model**: Scikit-learn Logistic Regression
- **Visualization**: CSS-based charts (fallback-friendly)

### Model Integration
- Uses existing `model.pkl` trained scikit-learn model
- Handles model loading errors gracefully with fallback predictions
- Real-time probability calculations for both on-time and delayed predictions

### Browser Compatibility
- Works without external CDN dependencies
- Pure CSS visualizations
- Responsive design for mobile and desktop

## Testing

Run the test suite:

```bash
python test_dashboard.py
```

Tests cover:
- Model prediction functionality  
- Airport data validation
- Dashboard component verification
- Parameter validation

## Files

- `simple_server.py` - Main dashboard server
- `test_dashboard.py` - Test suite for dashboard
- `server.py` - Original Flask API (requires Flask)
- `model.pkl` - Trained ML model
- `origin_airport.csv` - Airport data

## Screenshots

The dashboard provides a clean, professional interface with:
- Gradient background design
- Interactive form elements
- Large probability displays
- Visual donut chart
- Real-time statistics tracking