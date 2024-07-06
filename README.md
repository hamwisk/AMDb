---

# Andy's Movie Database (AMDb)

AMDb is a movie catalog program designed to help you organize your digital movie collection. Originally developed for my dad, this program is perfect for anyone with a digital movie library, offering a blend of automation and user control.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Description

AMDb is a user-friendly application designed to manage and explore your digital movie collection. The program is highly automated, making it easy for users, including those who are less tech-savvy, to catalog their movies efficiently without risking system stability.

## Installation

The program is written in Python and packaged as a standalone executable for Linux systems. Follow these steps to install AMDb:

1. Download the installer package from the [releases page](link-to-releases).
2. Ensure the installer has the correct permissions to run as an executable:
   ```bash
   chmod +x amdb_installer.run
   ```
3. Run the installer by double-clicking the icon or executing it via terminal:
   ```bash
   ./amdb_installer.run
   ```
4. Once installation is complete, a desktop shortcut will be created, and AMDb can be launched from the system's program menu.

For non-Linux systems or running the Python scripts directly, ensure Python is installed on your machine and run the following:
```bash
git clone https://github.com/yourusername/AMDb.git
cd AMDb
pip install -r requirements.txt
python main.py
```

## Usage

To launch AMDb, use the desktop shortcut or run the following command:
```bash
amdb
```

### Example Usage

- **Scanning Folders**: The program can recursively scan local folders to detect movie files, clean their filenames, and generate a list of potential entries.
- **Metadata Retrieval**: Uses OMDb API to fetch full metadata and poster images for selected movies. An OMDb API key is required, which can be obtained for free.
- **Search and Sort**: Comprehensive search options and sorting by title, release date, or date added.
- **View Modes**: Grid view for a visually appealing layout or list view for batch operations.

![Screenshot](screenshot.png)

## Features

- **Automated Movie Detection**: Recursively scans folders and detects movie files.
- **Metadata Retrieval**: Fetches full metadata and poster images from OMDb API.
- **Search Functionality**: Search by title, actors, director, writer, genre, rating, and release date.
- **Sorting and Viewing**: Sort by title, release date, or date added; choose between grid and list views.
- **Batch Operations**: Perform batch operations like adding/removing keywords, marking as watched/unwatched, path verification, and deletion.
- **Detailed Movie Dialogs**: View complete metadata, add personal ratings, view short or long plots, and access critic reviews from IMDb, Rotten Tomatoes, and Metacritic.

## Contributing

As this is my first GitHub project, I’m open to contributions and learning from the community. Here’s how you can contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

Feel free to report issues through the GitHub issues page.

## License

I haven’t decided on a license yet. If you have suggestions or guidance on this, I’d appreciate the input.

## Credits

AMDb was developed solely by me, inspired by my dad's extensive movie collection. The project uses Qt for the GUI and dual-threading, with Python handling the backend. Key libraries include `os` and `sys`.

---
