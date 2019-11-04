__all__ = ['setup']
__version__ = '1.0.0'


from cylc.sphinx_ext.cylc_domain.cylc_domain import CylcDomain


def setup(app):
    app.add_domain(CylcDomain)
    return {'version': __version__, 'parallel_read_safe': True}
