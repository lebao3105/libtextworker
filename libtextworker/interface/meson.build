opt = get_option('ui')

src = [
    '__init__.py',
    'manager.py'
]

install_data(
    src,
    install_dir: join_paths(
        moduledir,
        'interface'
    )
)

# No Tk support now
if opt == 'wx'
    subdir('wx')
endif