# Raw Material Development Assistant

A simple AI-powered assistant for processing RFQs (Request for Quotations) and finding suitable suppliers for raw materials.

## Setup

1. Install Ollama:
   ```bash
   curl https://ollama.ai/install.sh | sh
   ```

2. Pull the llama3 model:
   ```bash
   ollama pull llama3:8b
   ```

3. Create and activate virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # For Windows:
   .\venv\Scripts\activate
   # For Linux/Mac:
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   streamlit run main.py
   ```

## Features

- Process RFQ text using local Ollama LLM
- Extract key specifications from RFQs
- Maintain a local database of suppliers
- Match RFQ requirements with supplier capabilities
- Score suppliers based on purity match and delivery rating

## Usage

1. Start the application
2. In the sidebar, add suppliers by filling in their details
3. In the main panel, paste an RFQ text
4. Click "Process RFQ" to analyze the RFQ and find suitable suppliers

## Note

This is a simplified demo version focusing on core AI functionality. The actual implementation would include more sophisticated matching algorithms and additional features as described in the tech proposal.
