pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'libtextworker')
localedir = join_paths(get_option('prefix'), get_option('localedir'))

conf = configuration_data()
conf.set('LOCALEDIR', localedir)
conf.set('TOUCHED', true)
configure_file(
            input: '__init__.py',
           output: '__init__.py',
    configuration: conf,
          install: true,
      install_dir: moduledir
)

toplevel_sources = [
    '__init__.py',
    'general.py',
    'get_config.py'
]

install_data(toplevel_sources, install_dir: moduledir)

subdir('interface')
subdir('licenses')