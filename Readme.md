## Prerequisites
- Python 3.11 (for local setup)
- GitHub account

## Setup

### 0. Setup the PostgreSQL database for vector storing:
Execute the following script to setup the database:
  ```
  ./setup_pgvector.sh
  ```
### 1. Environment Variables:
Copy the sample environment file and edit it with your API keys:
   ```
   cp .env.sample .env
   ```
Edit the `.env` file and add your required variables:
   ```
   OPENAI_API_KEY=your_openai_key
   ```
Export your `.env` variables to the system:
   **Linux / Mac / Bash**
   ```
   export $(grep -v '^#' .env | xargs)
   ```
### Local Setup (Alternative to Docker):
1. Ensure you have Python 3.11+ installed.
2. Set up a virtual environment:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the main script:
   ```
   python main.py --repo-path /path/to/your/dir [--extra-files <fn1> <fn2>]

   Help:
   --repo-path    This is the absolute path to your repository.
   --extra-files  If you created a new file(s) that don't show up in a git diff or just an extra file from the repository.
   --no-db        Basically the script uses the database to store the reviews. But if you don't want to store it in the db just use this option.
   ```