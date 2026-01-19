# ScholarGraph Usage Guide (CLI)

This guide provides instructions on how to set up and use the ScholarGraph terminal utility.

## Prerequisites

- **Python 3.8+**
- **Google AI API Key**: Required for Gemini Pro. Get one at [Google AI Studio](https://aistudio.google.com/).
- **Environmental Variables**: Create a `.env` file in the root directory with your API key:
  ```env
  GEMINI_API_KEY=your_actual_api_key_here
  ```

## Installation

1. **Clone the repository** (if applicable).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the CLI

Use the `cli.py` script to process PDFs and generate a knowledge graph JSON file.

### Basic Usage

Process a single PDF:
```bash
python cli.py --input report.pdf --output graph.json
```

Process a directory of PDFs:
```bash
python cli.py --input ./papers --output global_graph.json
```

### Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--input` | `-i` | Path to a PDF file or directory. (Required) | - |
| `--output` | `-o` | Name of the output JSON file. | `graph_output.json` |
| `--threshold` | `-t` | Similarity threshold for cross-paper links (0-1). | `0.85` |

## Understanding the Output

The output is a JSON file compatible with `NetworkX`'s `node_link_data` format. It contains:
- `nodes`: List of concept nodes with `id`, `label`, `summary`, and `paper_title`.
- `links`: List of edges between nodes, categorized as `hierarchical` (within a paper) or `cross-paper` (semantically similar).
