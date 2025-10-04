# Setup Instructions

## Prerequisites

1. Python 3.11 or higher
2. Azure OpenAI API access
3. GitHub account with repository access
4. Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pr-reviewer-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the root directory:
```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
GITHUB_TOKEN=your_github_token
```

2. Configure the agent settings in `config/settings.yaml`:
```yaml
agent:
  review_timeout: 300  # seconds
  max_files: 100
  concurrent_reviews: 5

analysis:
  style_check: true
  security_check: true
  architecture_check: true
```

## Running the Agent

1. Start the agent:
```bash
python src/main.py
```

2. For development mode:
```bash
python src/main.py --dev
```

## Docker Deployment

1. Build the container:
```bash
docker build -t pr-reviewer-agent .
```

2. Run the container:
```bash
docker run -d --name pr-reviewer \
  -e AZURE_OPENAI_API_KEY=your_api_key \
  -e AZURE_OPENAI_ENDPOINT=your_endpoint \
  -e GITHUB_TOKEN=your_github_token \
  pr-reviewer-agent
```