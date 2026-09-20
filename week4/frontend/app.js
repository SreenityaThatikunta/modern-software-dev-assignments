async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes(query = '') {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = query ? `/notes/search?q=${encodeURIComponent(query)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    const label = document.createElement('span');
    label.textContent = `${n.title}: ${n.content} `;
    li.appendChild(label);
    const edit = document.createElement('button');
    edit.textContent = 'Edit';
    edit.onclick = async () => {
      const title = window.prompt('Title', n.title);
      const content = window.prompt('Content', n.content);
      if (title === null || content === null) return;
      await fetchJSON(`/notes/${n.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      loadNotes(document.getElementById('note-search').value);
    };
    li.appendChild(edit);
    const remove = document.createElement('button');
    remove.textContent = 'Delete';
    remove.onclick = async () => {
      if (!window.confirm(`Delete "${n.title}"?`)) return;
      await fetch(`/notes/${n.id}`, { method: 'DELETE' });
      loadNotes(document.getElementById('note-search').value);
    };
    li.appendChild(remove);
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById('note-search').addEventListener('input', (e) => {
    loadNotes(e.target.value);
  });

  loadNotes();
  loadActions();
});
