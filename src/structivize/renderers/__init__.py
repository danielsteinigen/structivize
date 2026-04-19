from importlib import import_module
import warnings

_DOMAIN_MODULES = [
	"biology",
	"business",
	"charts",
	"chemistry",
	"culture",
	"datastructure",
	"drawing",
	"electronics",
	"modeling",
]


def _safe_import(name: str) -> None:
	try:
		module = import_module(f"{__name__}.{name}")
		globals()[name] = module
	except ModuleNotFoundError as exc:
		missing = exc.name or ""
		if missing.startswith("structivize"):
			raise
		warnings.warn(
			f"Optional dependency missing for renderer domain '{name}': {missing}. "
			f"Install 'structivize[{name}]' or 'structivize[all]'.",
			RuntimeWarning,
		)


for _name in _DOMAIN_MODULES:
	_safe_import(_name)

__all__ = [name for name in _DOMAIN_MODULES if name in globals()]
