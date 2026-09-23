# Local Ollama Adapter

JudgeTrust includes a dependency-free adapter for Ollama's local
`/api/generate` endpoint. The default model is `qwen2.5:14b`, with streaming
disabled and temperature and seed fixed to zero. Ollama is asked for JSON and
the returned text is still checked by JudgeTrust's strict result parser.

The adapter does not start Ollama or download a model. Those remain explicit
operator actions. A real run should begin with a small smoke test before the
192-comparison pilot is attempted.

The project requires Python 3.10 or newer. On the development machine,
Homebrew Python 3.11 should be used instead of the macOS system Python 3.9.

