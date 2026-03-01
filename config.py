from dataclasses import dataclass

@dataclass
class Settings:
    base_url: str = "http://localhost:11434"
    temperature: float = 0.2

    patient_model: str = "phi4"
    supervisor_model: str = "phi4"

    ollama_options: dict = None

    def __post_init__(self):
        if self.ollama_options is None:
            self.ollama_options = {"num_gpu": 1, "num_ctx": 4096, "num_thread": 8}