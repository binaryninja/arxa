# arxa

arxa is a tool to automatically generate research reviews from an arXiv paper or a local PDF. It even supports optional GitHub repository cloning and analysis if a GitHub URL is detected in the review.

## Installation

You can install via pip:

`pip install arxa`

Then run it with the command-line interface as shown below.

## Features

Generate a review for a single arXiv paper by providing its ID:
`arxa -aid 1234.5678 -o output.md`

Generate a review from a local PDF file:
`arxa -pdf /path/to/paper.pdf -o output.md`

Specify the LLM backend provider and model:
`arxa -pdf /path/to/paper.pdf -o output.md -p openai -m o3-mini`

Enable GitHub cloning (disabled by default):
`arxa -pdf /path/to/paper.pdf -o output.md -g`

Use a configuration file for additional settings:
`arxa -c config.yaml`

### Minimal Configuration (config.yaml)

This minimal config specifies only the directories used by arxa.

```yaml
# config.yaml
papers_directory: "/tmp/arxa/papers"      # Directory to store or cache PDF files
output_directory: "/tmp/arxa/output"      # Directory where the generated reviews will be saved
```

---

### Advanced Configuration (config_advanced.yaml)

This extended example includes additional settings such as LLM parameters and logging options, which you can modify according to your needs.

```yaml
# config_advanced.yaml

# Directory where downloaded or generated PDF files will be stored
papers_directory: "/var/data/arxa/papers"

# Directory where output markdown reviews will be saved
output_directory: "/var/data/arxa/reviews"

# Optional LLM configuration settings
llm:
  provider: "openai"         # Options: "anthropic", "openai", "ollama"
  model: "o3-mini"           # Model identifier/version to be used for generating reviews
  max_prompt_tokens: 150000  # Maximum tokens to reserve for the prompt (if applicable)

# Logging configuration (customize as needed)
logging:
  level: "DEBUG"            # Options like: DEBUG, INFO, WARNING, etc.
  file: "/var/log/arxa.log"  # Log file path
```
