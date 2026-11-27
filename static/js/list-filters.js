/* Filters, sort button and counter for lists of publications, talks and projects.
 *
 * The partial "list_filters" makes the controls. Each item of the list has
 * the attribute "data-list-item" and these attributes (partial "list_item_data"):
 *   data-date  the date as a number, for example "20180923"
 *   data-tags  the tags, for example "rdf shex"
 *   data-type  the publication type, for example "2" (optional)
 *   data-text  the text for the text search (optional)
 * An element with "data-list-group" groups items, for example the talks of one
 * year. A group with no visible items is hidden.
 *
 * The URL hash keeps the filters and the order, for example "#2",
 * "#tag=rdf", "#2&tag=rdf&sort=oldest" or "#q=wikidata".
 */
(function () {
  'use strict';

  // Lower case, with no accents and ligatures: "Lógica" -> "logica".
  function simpleText(text) {
    return (text || '').normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  function setup(root) {
    var list = document.querySelector(root.getAttribute('data-list'));
    if (!list) { return; }
    var noun = root.getAttribute('data-noun') || 'items';
    var items = Array.prototype.slice.call(list.querySelectorAll('[data-list-item]'));
    var groups = Array.prototype.slice.call(list.querySelectorAll('[data-list-group]'));
    items.forEach(function (item, i) {
      item.listIndex = i;
      item.listTags = (item.getAttribute('data-tags') || '').split(/\s+/).filter(Boolean);
      item.listText = simpleText(item.getAttribute('data-text') || item.textContent);
    });
    groups.forEach(function (group, i) { group.listIndex = i; });

    var typeSelect = root.querySelector('.list-type');
    var textSearch = root.querySelector('.list-text-search');
    var sortButton = root.querySelector('.list-sort');
    var counter = root.querySelector('.list-count');
    var tagSelect = root.querySelector('.list-tags-select');
    var tagSearch = root.querySelector('.list-tag-search');
    var tagResults = root.querySelector('.list-tag-results');
    var tagClear = root.querySelector('.list-tag-clear');
    var tagCurrent = root.querySelector('.list-tag-current');
    var chips = Array.prototype.slice.call(root.querySelectorAll('.list-tag-chip'));
    var tagOptions = tagSelect ? Array.prototype.slice.call(tagSelect.options).filter(function (o) {
      return o.value != '*';
    }).map(function (o) {
      return { value: o.value, label: o.textContent.trim(), key: simpleText(o.textContent) };
    }) : [];

    var state = { type: '*', tag: '*', text: '', order: 'newest' };

    // Show the items that pass all the filters, in the selected order.
    function render() {
      // Each word of the search must be in the text of the item, in any order.
      var words = simpleText(state.text).split(/\s+/).filter(Boolean);
      var shown = 0;
      items.forEach(function (item) {
        var ok = (state.type == '*' || item.getAttribute('data-type') == state.type) &&
                 (state.tag == '*' || item.listTags.indexOf(state.tag) >= 0) &&
                 words.every(function (w) { return item.listText.indexOf(w) >= 0; });
        item.hidden = !ok;
        if (ok) { shown++; }
      });
      groups.forEach(function (group) {
        group.hidden = !group.querySelector('[data-list-item]:not([hidden])');
      });
      sortElements(items);
      sortElements(groups);
      if (counter) {
        counter.textContent = 'Showing ' + shown + ' of ' + items.length + ' ' + noun;
      }
      updateControls();
    }

    // The page has the newest items first. For the oldest first, sort by
    // date and keep items with the same date in the reverse page order.
    function sortElements(elements) {
      var sorted = elements.slice().sort(function (a, b) {
        if (state.order == 'oldest') {
          var da = a.getAttribute('data-date') || '', db = b.getAttribute('data-date') || '';
          if (da != db) { return da < db ? -1 : 1; }
          return b.listIndex - a.listIndex;
        }
        return a.listIndex - b.listIndex;
      });
      sorted.forEach(function (el) { el.parentNode.appendChild(el); });
    }

    function updateControls() {
      if (typeSelect) { typeSelect.value = state.type; }
      if (textSearch && textSearch.value != state.text) { textSearch.value = state.text; }
      if (sortButton) {
        sortButton.setAttribute('data-order', state.order);
        sortButton.querySelector('.list-sort-label').textContent = state.order == 'oldest' ? 'Oldest first' : 'Newest first';
        var icon = sortButton.querySelector('.fa');
        if (icon) {
          icon.classList.toggle('fa-sort-amount-desc', state.order != 'oldest');
          icon.classList.toggle('fa-sort-amount-asc', state.order == 'oldest');
        }
      }
      if (tagSelect) {
        tagSelect.value = state.tag;
        var option = tagSelect.options[tagSelect.selectedIndex];
        tagCurrent.textContent = option ? option.textContent.trim() : '';
        tagClear.hidden = state.tag == '*';
        chips.forEach(function (chip) {
          chip.classList.toggle('active', chip.getAttribute('data-tag') == state.tag);
        });
      }
    }

    // URL hash <-> state.
    // A new hash makes a history entry, so the back button undoes a filter.
    // Typing in the text search replaces the entry instead.
    function writeHash(replace) {
      var hash = [];
      if (state.type != '*') { hash.push(state.type); }
      if (state.tag != '*') { hash.push('tag=' + state.tag); }
      if (state.text.trim() != '') { hash.push('q=' + encodeURIComponent(state.text.trim())); }
      if (state.order == 'oldest') { hash.push('sort=oldest'); }
      var newHash = hash.length ? '#' + hash.join('&') : '';
      if (newHash == window.location.hash) { return; }
      if (newHash == '' || replace) {
        history.replaceState(null, '', window.location.pathname + window.location.search + newHash);
      } else {
        window.location.hash = newHash;
      }
    }

    function readHash() {
      state = { type: '*', tag: '*', text: '', order: 'newest' };
      window.location.hash.replace(/^#/, '').split('&').forEach(function (part) {
        if (part != '' && !isNaN(part) && typeSelect) {
          state.type = part;
        } else if (part.indexOf('tag=') == 0 && tagSelect) {
          var name = part.substr(4);
          if (tagOptions.some(function (o) { return o.value == name; })) { state.tag = name; }
        } else if (part.indexOf('q=') == 0 && textSearch) {
          try { state.text = decodeURIComponent(part.substr(2)); } catch (e) { state.text = part.substr(2); }
        } else if (part == 'sort=oldest') {
          state.order = 'oldest';
        }
      });
      if (typeSelect && !typeSelect.querySelector('option[value="' + state.type + '"]')) { state.type = '*'; }
      render();
    }

    function change(update, replace) {
      Object.keys(update).forEach(function (k) { state[k] = update[k]; });
      render();
      writeHash(replace);
    }

    if (typeSelect) {
      typeSelect.addEventListener('change', function () { change({ type: typeSelect.value }); });
    }
    if (textSearch) {
      textSearch.addEventListener('input', function () { change({ text: textSearch.value }, true); });
    }
    if (sortButton) {
      sortButton.addEventListener('click', function () {
        change({ order: state.order == 'oldest' ? 'newest' : 'oldest' });
      });
    }

    // Search box for tags: the list shows the tags that contain the text.
    // Tags that start with the text come first.
    function selectTag(value) {
      tagSearch.value = '';
      tagResults.hidden = true;
      change({ tag: value });
    }

    function showTagResults() {
      var text = simpleText(tagSearch.value.trim());
      var matches = tagOptions.filter(function (o) { return o.key.indexOf(text) >= 0; });
      matches.sort(function (a, b) {
        return (b.key.indexOf(text) == 0) - (a.key.indexOf(text) == 0);
      });
      tagResults.innerHTML = '';
      if (matches.length == 0) {
        var empty = document.createElement('li');
        empty.className = 'empty';
        empty.textContent = 'No tags found';
        tagResults.appendChild(empty);
      }
      matches.forEach(function (o) {
        var li = document.createElement('li');
        li.setAttribute('role', 'option');
        li.setAttribute('data-value', o.value);
        li.textContent = o.label;
        tagResults.appendChild(li);
      });
      tagResults.hidden = false;
    }

    if (tagSearch) {
      tagSearch.addEventListener('input', showTagResults);
      tagSearch.addEventListener('focus', showTagResults);
      tagSearch.addEventListener('blur', function () { tagResults.hidden = true; });
      tagSearch.addEventListener('keydown', function (e) {
        var options = Array.prototype.slice.call(tagResults.querySelectorAll('li[data-value]'));
        var active = tagResults.querySelector('li.active');
        var index = options.indexOf(active);
        if (e.key == 'ArrowDown' || e.key == 'ArrowUp') {
          e.preventDefault();
          if (tagResults.hidden) {
            showTagResults();
            options = Array.prototype.slice.call(tagResults.querySelectorAll('li[data-value]'));
          }
          index = e.key == 'ArrowDown' ? Math.min(index + 1, options.length - 1) : Math.max(index - 1, 0);
          options.forEach(function (o) { o.classList.remove('active'); });
          if (options[index]) {
            options[index].classList.add('active');
            options[index].scrollIntoView({ block: 'nearest' });
          }
        } else if (e.key == 'Enter') {
          e.preventDefault();
          var choice = active || options[0];
          if (choice) { selectTag(choice.getAttribute('data-value')); }
        } else if (e.key == 'Escape') {
          tagResults.hidden = true;
        }
      });
      // Use mousedown, so that the selection comes before the search box loses the focus.
      tagResults.addEventListener('mousedown', function (e) {
        var li = e.target.closest('li[data-value]');
        if (li) {
          e.preventDefault();
          selectTag(li.getAttribute('data-value'));
        }
      });
      tagClear.addEventListener('click', function () { selectTag('*'); });
      chips.forEach(function (chip) {
        chip.addEventListener('click', function () {
          var value = chip.getAttribute('data-tag');
          // A second click on the selected tag shows all the items again.
          selectTag(state.tag == value ? '*' : value);
        });
      });
    }

    window.addEventListener('hashchange', readHash);
    readHash();
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.list-filters'), setup);
  }

  if (document.readyState == 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
