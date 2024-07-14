---

# Andy's Movie Database (AMDb)

AMDb is a versatile movie catalog program designed to help you organize your digital movie collection across multiple platforms. Originally developed for personal use, this program is ideal for anyone with a digital movie library, offering a blend of automation and user control.

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

The program is written in Python and packaged as a standalone executable for Windows, macOS, and Linux systems. Follow these steps to install AMDb:

### Windows
1. Download the installer package from the [releases page](https://github.com/hamwisk/AMDb/releases).
2. Run the installer and follow the on-screen instructions.
3. Once installation is complete, a desktop shortcut will be created, and AMDb can be launched from the Start menu.

### macOS
1. Download the installer package from the [releases page](https://github.com/hamwisk/AMDb/releases).
2. Open the downloaded .dmg file and drag AMDb to your Applications folder.
3. Launch AMDb from the Applications folder or Spotlight search.

### Linux
1. Download the installer package from the [releases page](https://github.com/hamwisk/AMDb/releases).
2. Ensure the installer has the correct permissions to run as an executable:
   ```bash
   chmod +x amdb_installer.run
   ```
3. Run the installer by double-clicking the icon or executing it via terminal:
   ```bash
   ./amdb_installer.run
   ```
4. Once installation is complete, a desktop shortcut will be created, and AMDb can be launched from the system's program menu.

For running the Python scripts directly, ensure Python is installed on your machine and run the following:
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
- **View Modes**: Grid view for a visually appealing layout or list view for editing and batch operations.

[Screenshot](https://github.com/hamwisk/AMDb/blob/main/images/Screenshot%20from%202024-07-06%2006-30-43.png)
[Screenshot](https://github.com/hamwisk/AMDb/blob/main/images/Screenshot%20from%202024-07-06%2006-37-00.png)
[Screenshot](https://github.com/hamwisk/AMDb/blob/main/images/Screenshot%20from%202024-07-06%2006-40-22.png)

## Features

- **Cross-Platform Support**: Available for Windows, macOS, and Linux.
- **Automated Movie Detection**: Recursively scans folders and detects movie files.
- **Metadata Retrieval**: Fetches full metadata and poster images from OMDb API.
- **Search Functionality**: Search by title, actors, director, writer, genre, rating, and release date.
- **Sorting and Viewing**: Sort by title, release date, or date added; choose between grid and list views.
- **Batch Operations**: Perform batch operations like adding/removing keywords, marking as watched/unwatched, path verification, and deletion.
- **Detailed Movie Dialogs**: View complete metadata, add personal ratings, view short or long plots, and access critic reviews from IMDb, Rotten Tomatoes, and Metacritic.

## Contributing

We welcome contributions from the community. Here’s how you can contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

Feel free to report issues through the GitHub issues page.

## License

AMDb is licensed under the MIT License. For more information, see the LICENSE file.

## Credits

AMDb was developed by the AMDb team, inspired by a passion for movies and efficient data management. The project uses an SQL database, Qt for the GUI, and Python for the backend.

---
