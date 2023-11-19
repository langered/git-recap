from typing import Any

import yaml
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """Load yaml."""

    def __call__(self) -> dict[str, Any]:  # noqa: WPS210
        """Load settings yaml."""
        yaml_settings: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name,
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex,
            )
            if field_value is not None:
                yaml_settings[field_key] = field_value

        return yaml_settings

    def get_field_value(
        self, field: FieldInfo, field_name: str,
    ) -> tuple[Any, str, bool]:
        """Get values from yaml file."""
        with open('settings.yaml', 'r') as yaml_config_file:
            yaml_data = yaml.safe_load(yaml_config_file)

        field_value = yaml_data.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool,  # noqa: WPS110
    ) -> Any:
        """Prepare field value."""
        return value


class Settings(BaseSettings):
    """Coniguration for git-recap."""

    model_config = SettingsConfigDict(env_file='settings.env', env_file_encoding='utf-8')

    # env variables
    github_host: str
    github_token: str
    recap_days: int = 1

    # variables from settings file
    repos_to_exclude: list[str] = []

    @classmethod
    def settings_customise_sources(  # noqa: WPS211
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Configure custom settings resources."""
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
