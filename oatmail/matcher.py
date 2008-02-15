import pkg_resources

def call_matcher(
    name,
    cfg,
    depot,
    folder,
    path,
    args,
    ):
    fn = None
    for entrypoint in \
            pkg_resources.iter_entry_points('oatmail.matcher', name):
        fn = entrypoint.load()

    if fn is None:
        raise RuntimeError('Command unknown: %s' % name)

    data = fn(
        cfg=cfg,
        depot=depot,
        folder=folder,
        path=path,
        args=args,
        )
    return data
