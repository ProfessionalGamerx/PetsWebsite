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