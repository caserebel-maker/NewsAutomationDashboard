# Project Handover / Transfer Guide

## 1. Before Leaving (At Home)

You have two main options to transfer your work. **Option A** is the best practice.

### Option A: Using Git (Recommended)
1.  **Commit your changes**:
    ```bash
    git add .
    git commit -m "Save progress for office"
    git push origin main
    ```
2.  **Backup the `.env` file**:
    *   **CRITICAL**: Your `.env` file containing API keys might be ignored by version control (check `.gitignore`).
    *   **Action**: Copy the content of `.env` to a secure note (Keep, Notes, etc.) or email it to yourself.
3.  **Backup the Database (Optional)**:
    *   If you need the history of news items (`news_database.db`), copy this file to a USB drive or cloud storage (Google Drive). It is likely ignored by Git.

### Option B: The "Copy Everything" Method
1.  Compress/Zip the entire `SportsNewsAuto` folder.
2.  **Exclude** the `.venv` folder if possible (it makes the zip huge and won't work on a different computer anyway).
3.  Upload the Zip to Google Drive or put it on a USB stick.

---

## 2. Setting Up (At Office)

### Prerequisites
*   Ensure **Python 3.10+** is installed on the office computer.

### Step-by-Step Setup
1.  **Get the Code**:
    *   *If utilizing Git*: `git clone <your-repo-url>`
    *   *If utilizing Zip*: Extract the folder.

2.  **Restore Critical Files**:
    *   Create a file named `.env` in the `SportsNewsAuto` folder.
    *   Paste your API keys into it.
    *   (Optional) Place `news_database.db` in the folder if you brought it.

3.  **Create Virtual Environment**:
    Open a terminal/command prompt in the `SportsNewsAuto` folder:
    ```bash
    # Create the environment
    python -m venv .venv
    
    # Activate it (Windows)
    .venv\Scripts\activate
    
    # Activate it (Mac/Linux)
    source .venv/bin/activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 3. How to Run
Once installed, you can resume work by running:
```bash
python scheduler.py
# or
streamlit run app.py
```
