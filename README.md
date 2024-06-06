# DBC Viewer

DBC Viewer is a graphical user interface (GUI) application for loading, viewing, editing, and saving DBC (DataBase CAN) files. The application is built using Python's `tkinter` library for the GUI and `cantools` for handling DBC files.

## Features

- **Load DBC File**: Load and display the content of a DBC file.
- **Save DBC File**: Save the modified DBC file.
- **Add Signal**: Add a new signal to the DBC file.
- **Delete Signal**: Delete an existing signal from the DBC file.
- **Edit Signal**: Edit the properties of an existing signal.
- **Copy Signal**: Copy an existing signal.

## Usage

1. **Run the application**:

   ```
   python main.py
   ```

2. **Load a DBC file**:

   - Click on the "Load DBC File" button.
   - Select a DBC file from the file dialog.

3. **View DBC content**:

   - The content of the DBC file is displayed in a table format.
   - Each row represents a signal within a message.

4. **Edit a signal**:

   - Double-click on a signal row to open the edit window.
   - Modify the properties and click "Save" to apply the changes.

5. **Add a new signal**:

   - Click on the "Add Signal" button.
   - Fill in the properties in the new window and click "Add".

6. **Delete a signal**:

   - Select a signal row and click on the "Delete Signal" button.

7. **Copy a signal**:

   - Right-click on a signal row and select "Copy" from the context menu.
   - A copy of the signal will be added with `_copy` suffix in the name.

8. **Save the DBC file**:

   - Click on the "Save DBC File" button.
   - Choose the location and name for the new DBC file.

## Files

- `main.py`: The main script containing the DBC Editor class and application logic.
- `requirements.txt`: The file listing the required Python packages.