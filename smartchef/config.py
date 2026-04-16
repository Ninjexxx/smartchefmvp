from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    spoonacular_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    demo_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_spoonacular(self) -> bool:
        return bool(self.spoonacular_api_key)


settings = Settings()
