# D&D Character Creator - Frontend

🎲 React-based frontend for the D&D Character Creator system.

## Quick Start

### 1. Setup & Install Dependencies
```bash
# Run the setup script
./setup.sh

# Or manually:
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The app will be available at `http://localhost:5173`

### 3. Backend Connection
Make sure your backend is running at `http://localhost:8000`. The frontend will automatically connect to the backend API.

## Project Structure

```
src/
├── components/           # React components
│   ├── Character/       # Character-related components
│   ├── DM/             # DM tools and admin features
│   ├── Journal/        # Character journal system
│   ├── common/         # Shared UI components
│   └── pages/          # Page-level components
├── services/           # API services
│   └── api.js         # Backend API integration
├── utils/             # Utility functions
├── App.jsx            # Main application component
├── main.jsx           # React entry point
└── index.css          # Global styles
```

## Key Features

- **Character Creation**: Step-by-step character builder with AI suggestions
- **Character Management**: View, edit, and manage characters
- **DM Tools**: Create NPCs, creatures, and manage content
- **Journal System**: Track character progression and story
- **API Integration**: Full backend integration with error handling

## Development Commands

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Environment Variables

Create `.env.local` for local overrides:
```
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

## Backend API Endpoints

The frontend connects to these backend endpoints:
- `GET /api/v1/characters` - List characters
- `POST /api/v1/characters` - Create character
- `PUT /api/v1/characters/{id}` - Update character
- `DELETE /api/v1/characters/{id}` - Delete character
- `POST /api/v1/generate/backstory` - Generate AI backstory
- `POST /api/v1/generate/equipment` - Generate AI equipment

## Next Steps

1. Start the development server: `npm run dev`
2. Open `http://localhost:5173` in your browser
3. Make sure backend is running at `http://localhost:8000`
4. Begin developing new features or customizing existing ones

## Tips

- Use the browser's developer tools to debug API calls
- Check the console for connection status and errors
- Modify `src/services/api.js` to add new API endpoints
- Add new components in the appropriate subdirectory
