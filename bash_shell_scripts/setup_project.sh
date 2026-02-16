#!/bin/bash

# Define project name
PROJECT_NAME="news-translator-pipeline"

echo "🚀 Starting setup for $PROJECT_NAME..."

# 1. Create Directory Structure
mkdir -p $PROJECT_NAME/credentials
mkdir -p $PROJECT_NAME/data

cd $PROJECT_NAME

# 2. Create empty files
touch .env
touch translator_utils.py
touch test_run.py

# 3. Create a sample news JSON file
cat <<EOF > data/sample_news.json
{
  "article_id": "101",
  "title": "New Breakthrough in AI Technology",
  "content": "Researchers have discovered a more efficient way to train large language models."
}
EOF

# 4. Set up Virtual Environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv

# 5. Activate venv and install dependencies
# Note: We use 'source' for the current shell, but inside a script we call pip directly from the bin
./venv/bin/pip install --upgrade pip
./venv/bin/pip install google-cloud-translate python-dotenv boto3

# 6. Final Instructions
echo "------------------------------------------------"
echo "✅ Setup Complete!"
echo "1. Move your 'google_key.json' into the '$PROJECT_NAME/credentials/' folder."
echo "2. Add your key path to the .env file."
echo "3. Run 'source venv/bin/activate' to start working."
echo "------------------------------------------------"
