const banner = document.querySelector('[data-testid="banner"]');
const list = document.querySelector('[data-testid="items"]');
const error = document.querySelector('[data-testid="error"]');

async function getJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} returned ${res.status}`);
  return res.json();
}

async function render() {
  const [version, data] = await Promise.all([getJson('/api/version'), getJson('/api/items')]);

  banner.textContent = `Preview environment · PR #${version.pr} · ${version.commit}`;
  banner.dataset.pr = version.pr;
  banner.dataset.commit = version.commit;

  list.replaceChildren(
    ...data.items.map((item) => {
      const li = document.createElement('li');
      li.dataset.status = item.status;
      li.textContent = item.title;
      return li;
    }),
  );
}

render().catch((err) => {
  banner.textContent = 'Preview environment · API unreachable';
  error.hidden = false;
  error.textContent = err.message;
});
