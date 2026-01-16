# Background Remover Web App

A web application that automatically removes backgrounds from images using [rembg](https://github.com/danielgatis/rembg).

## Features

- 🎨 Automatic background removal
- 📸 Drag and drop image upload
- 💾 Download processed images
- 🎯 Clean and modern UI
- ⚡ Fast processing with rembg

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd rembg-web
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Open your browser and go to:
```
http://localhost:5001
```

**Note:** Port 5000 is often used by macOS AirPlay Receiver, so the app uses port 5001 by default.

3. Upload an image and wait for processing!

## Deployment

### Deploy to Heroku

1. Create a `Procfile`:
```
web: python app.py
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Deploy to Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect and deploy the Flask app

### Deploy to Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI Model**: rembg (U²-Net)

## License

MIT License
