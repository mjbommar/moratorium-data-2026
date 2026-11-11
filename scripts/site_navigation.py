"""Shared navigation for the dashboard and generated reference pages."""

def navigation(prefix='', current='index.html'):
    links = [('index.html#explore', 'Explore'), ('states/index.html', 'States'),
             ('docs/ballot-results.html', 'Ballot measures'), ('data/index.html', 'Data'),
             ('docs/FAQ.html', 'About the data')]
    items = []
    for target, label in links:
        active = current == target.split('#')[0] or (target.startswith('states/') and current.startswith('states/'))
        items.append(f'<a href="{prefix}{target}"' + (' aria-current="page"' if active else '') + f'>{label}</a>')
    return f'''<header class="site-header">
  <div class="site-header-inner">
    <a class="site-brand" href="{prefix}index.html">Moratorium Nation</a>
    <details class="site-menu"><summary>Menu</summary>
      <nav aria-label="Main navigation">{''.join(items)}</nav>
    </details>
    <button class="theme-toggle" id="theme-toggle" type="button" aria-pressed="false" hidden><span class="theme-indicator" aria-hidden="true"></span>Dark mode</button>
  </div>
</header>'''
