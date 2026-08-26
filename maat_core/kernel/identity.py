from maat_core.kernel._load import export_module

_m = export_module("identity")
IdentityStore = _m.IdentityStore

__all__ = ["IdentityStore"]
