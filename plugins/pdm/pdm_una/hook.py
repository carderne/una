from pdm.backend.hooks import Context

from pdm_una.include import force_include
from pdm_una.meta import add_dependencies


def pdm_build_initialize(context: Context):
    add_dependencies(context)
    force_include(context)
