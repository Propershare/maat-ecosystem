from maat_core.kernel._load import export_module

_m = export_module("policy")
PolicyEngine = _m.PolicyEngine

__all__ = ["PolicyEngine"]
