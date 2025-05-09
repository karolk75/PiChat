# PiChat Frontend

A modern, responsive chat application built with React, TypeScript, and Vite.

## Features

- Real-time chat functionality using WebSockets
- Responsive design with Tailwind CSS
- Dark mode support
- Markdown rendering for chat messages

## Tech Stack

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Routing**: React Router
- **Real-time Communication**: Socket.io
- **UI Components**: Radix UI
- **Animations**: Framer Motion
- **Code Quality**: ESLint, TypeScript

## Prerequisites

- Node.js (v16 or later)
- npm or yarn

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pichat-frontend.git
cd pichat-frontend

# Install dependencies
npm install
# or
yarn install
```

### Development

```bash
# Start the development server
npm run dev
# or
yarn dev
```

The application will be available at http://localhost:8501.

### Building for Production

```bash
# Build the application
npm run build
# or
yarn build

# Preview the built application
npm run preview
# or
yarn preview
```

### Serving the Production Build

```bash
# Serve the built application
npm run serve
# or
yarn serve
```

The application will be served at http://localhost:8501.

## Project Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── assets/      # Images, fonts, etc.
│   ├── components/  # Reusable UI components
│   ├── context/     # React Context providers
│   ├── hooks/       # Custom React hooks
│   ├── interfaces/  # TypeScript interfaces
│   ├── lib/         # Utility functions and libraries
│   ├── pages/       # Page components
│   ├── service/     # API services
│   ├── App.tsx      # Main application component
│   └── main.tsx     # Application entry point
├── index.html       # HTML template
├── package.json     # Project dependencies and scripts
└── vite.config.ts   # Vite configuration
```

## Configuration

The application can be configured through environment variables. Create a `.env` file in the root directory of the project with the following variables:

```
VITE_API_URL=your_backend_api_url
VITE_WS_URL=your_websocket_url
```

## Docker

See the [Dockerfile](./Dockerfile) for containerization details. To build and run the Docker container:

```bash
# Build the Docker image
docker build -t pichat-frontend .

# Run the container
docker run -p 8501:8501 pichat-frontend
```