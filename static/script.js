function filterItems() {
    const input = document.getElementById('search-input');
    const filter = input.value.toLowerCase();
    const items = document.getElementsByClassName('item');

    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        const text = item.textContent || item.innerText;
        if (text.toLowerCase().indexOf(filter) > -1) {
            item.style.display = "";
        } else {
            item.style.display = "none";
        }
    }
}

function showSuggestions() {
    const input = document.getElementById('search-input');
    const val = input.value.toLowerCase();
    const list = document.getElementById('autocomplete-list');
    list.innerHTML = '';
    if (!val) return;

    const matches = petNames.filter(name => name.toLowerCase().includes(val));
    matches.forEach(name => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.innerHTML = name;
        item.onclick = function() {
            input.value = name;
            list.innerHTML = '';
        };
        list.appendChild(item);
    });
}

// Closes dropdown if user clicks outside
window.addEventListener('click', function(e) {
    if (!e.target.matches('#search-input')) {
        document.getElementById('autocomplete-list').innerHTML = '';
    }
});

// On enter, search for the pet and redirect to its detail page
const searchInput = document.getElementById('search-input');
if (searchInput) {
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim().toLowerCase();
            // Find the pet name (case-insensitive exact match)
            let found = null;
            for (let i = 0; i < petNames.length; i++) {
                if (petNames[i].toLowerCase() === query) {
                    found = petNames[i];
                    break;
                }
            }
            if (found) {
                // Find which table the pet is in and its id
                fetch(`/find_pet?name=${encodeURIComponent(found)}`)
                  .then(res => res.json())
                  .then(data => {
                    if (data && data.table && data.id) {
                      window.location.href = `/item/${data.table}/${data.id}`;
                    }
                  });
            }
        }
    });
}