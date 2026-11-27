/*************************************************
 *  Academic: the personal website framework for Hugo.
 *  https://github.com/gcushen/hugo-academic
 **************************************************/

(function($){

  /* ---------------------------------------------------------------------------
   * Responsive scrolling for URL hashes.
   * --------------------------------------------------------------------------- */

  // Dynamically get responsive navigation bar offset.
  let $navbar = $('.navbar-header');
  let navbar_offset = $navbar.innerHeight();

  /**
   * Responsive hash scrolling.
   * Check for a URL hash as an anchor.
   * If it exists on current page, scroll to it responsively.
   * If `target` argument omitted (e.g. after event), assume it's the window's hash.
   */
  function scrollToAnchor(target) {
    // If `target` is undefined or HashChangeEvent object, set it to window's hash.
    target = (typeof target === 'undefined' || typeof target === 'object') ? window.location.hash : target;
    // Escape colons from IDs, such as those found in Markdown footnote links.
    target = target.replace(/:/g, '\\:');

    // The hash is not always an element ID (for example "#tag=rdf" in the
    // publication filters). Then do nothing.
    let $target;
    try {
      $target = $(target);
    } catch (e) {
      return;
    }

    // If target element exists, scroll to it taking into account fixed navigation bar offset.
    if($target.length) {
      $('body').addClass('scrolling');
      $('html, body').animate({
        scrollTop: $target.offset().top - navbar_offset
      }, 600, function () {
        $('body').removeClass('scrolling');
      });
    }
  }

  // Make Scrollspy responsive.
  function fixScrollspy() {
    let $body = $('body');
    let data = $body.data('bs.scrollspy');
    if (data) {
      data.options.offset = navbar_offset;
      $body.data('bs.scrollspy', data);
      $body.scrollspy('refresh');
    }
  }

  // Check for hash change event and fix responsive offset for hash links (e.g. Markdown footnotes).
  window.addEventListener("hashchange", scrollToAnchor);

  /* ---------------------------------------------------------------------------
   * Add smooth scrolling to all links inside the main navbar.
   * --------------------------------------------------------------------------- */

  $('#navbar-main li.nav-item a').on('click', function(event) {
    // Store requested URL hash.
    let hash = this.hash;

    // If we are on the homepage and the navigation bar link is to a homepage section.
    if ( hash && $(hash).length && ($("#homepage").length > 0)) {
      // Prevent default click behavior.
      event.preventDefault();

      // Use jQuery's animate() method for smooth page scrolling.
      // The numerical parameter specifies the time (ms) taken to scroll to the specified hash.
      $('html, body').animate({
        scrollTop: $(hash).offset().top - navbar_offset
      }, 800);
    }
  });

  /* ---------------------------------------------------------------------------
   * Smooth scrolling for Back To Top link.
   * --------------------------------------------------------------------------- */

  $('#back_to_top').on('click', function(event) {
    event.preventDefault();
    $('html, body').animate({
      'scrollTop': 0
    }, 800, function() {
      window.location.hash = "";
    });
  });

  /* ---------------------------------------------------------------------------
   * Hide mobile collapsable menu on clicking a link.
   * --------------------------------------------------------------------------- */

  $(document).on('click', '.navbar-collapse.in', function(e) {
    //get the <a> element that was clicked, even if the <span> element that is inside the <a> element is e.target
    let targetElement = $(e.target).is('a') ? $(e.target) : $(e.target).parent();

    if (targetElement.is('a') && targetElement.attr('class') != 'dropdown-toggle') {
      $(this).collapse('hide');
    }
  });

  /* ---------------------------------------------------------------------------
   * Filter projects.
   * --------------------------------------------------------------------------- */

  let $grid_projects = $('#container-projects');
  $grid_projects.imagesLoaded(function () {
    // Initialize Isotope after all images have loaded.
    $grid_projects.isotope({
      itemSelector: '.isotope-item',
      layoutMode: 'masonry'
    });

    // Filter items when filter link is clicked.
    $('#filters a').click(function () {
      let selector = $(this).attr('data-filter');
      $grid_projects.isotope({filter: selector});
      $(this).removeClass('active').addClass('active').siblings().removeClass('active all');
      return false;
    });
  });

  /* ---------------------------------------------------------------------------
   * Filter publications.
   * --------------------------------------------------------------------------- */

  let $grid_pubs = $('#container-publications');
  $grid_pubs.isotope({
    itemSelector: '.isotope-item',
    percentPosition: true,
    masonry: {
      // Use Bootstrap compatible grid layout.
      columnWidth: '.grid-sizer'
    }
  });

  // Filter publications by type and by tag. The filter of Isotope is the
  // class of the type and the class of the tag, for example ".pubtype-2.tag-1a2b".
  function apply_publication_filters() {
    let type = $('.pub-filters-select').val() || '*';
    let tag = $('.pub-tags-select').val() || '*';
    let filterValue = [type, tag].filter(function (f) { return f != '*'; }).join('');
    $grid_pubs.isotope({ filter: filterValue || '*' });

    // Set hash URL to current filters, for example "#2", "#tag=rdf" or "#2&tag=rdf".
    let hash = [];
    if (type.substr(0, 9) == '.pubtype-') {
      hash.push(type.substr(9));
    }
    let tagName = $('.pub-tags-select option:selected').attr('data-tag');
    if (tag != '*' && tagName) {
      hash.push('tag=' + tagName);
    }
    if (hash.length > 0) {
      window.location.hash = hash.join('&');
    } else if (window.location.hash) {
      history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  }

  // Bind publication filters on dropdown change.
  $('.pub-filters-select, .pub-tags-select').on('change', function () {
    apply_publication_filters();
    update_tag_search();
  });

  /* ---------------------------------------------------------------------------
   * Search box and buttons for the tag filter.
   * The hidden select ".pub-tags-select" has the tags and the selected tag.
   * --------------------------------------------------------------------------- */

  // Lower case, with no accents and ligatures: "Lógica" -> "logica".
  function simple_text(text) {
    return text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }

  let $tag_search = $('.pub-tag-search');
  let $tag_results = $('.pub-tag-results');
  let tag_options = $('.pub-tags-select option').filter(function () {
    return this.value != '*';
  }).map(function () {
    return { value: this.value, label: $(this).text().trim(), key: simple_text($(this).text()) };
  }).get();

  function select_tag(value) {
    $('.pub-tags-select').val(value).trigger('change');
    $tag_search.val('');
    $tag_results.prop('hidden', true);
  }

  // Show the tags that contain the text in the search box. Tags that start
  // with the text come first.
  function show_tag_results() {
    let text = simple_text($tag_search.val().trim());
    let matches = tag_options.filter(function (o) { return o.key.indexOf(text) >= 0; });
    matches.sort(function (a, b) {
      return (b.key.indexOf(text) == 0) - (a.key.indexOf(text) == 0);
    });
    $tag_results.empty();
    if (matches.length == 0) {
      $tag_results.append($('<li class="empty">').text('No tags found'));
    }
    matches.forEach(function (o) {
      $tag_results.append($('<li role="option">').attr('data-value', o.value).text(o.label));
    });
    $tag_results.prop('hidden', false);
  }

  // Show the selected tag on the clear button and on the buttons of the most used tags.
  function update_tag_search() {
    let value = $('.pub-tags-select').val() || '*';
    let label = $('.pub-tags-select option:selected').text().trim();
    $('.pub-tag-current').text(label);
    $('.pub-tag-clear').prop('hidden', value == '*');
    $('.pub-tag-chip').each(function () {
      $(this).toggleClass('active', $(this).attr('data-value') == value);
    });
  }

  $tag_search.on('input focus', show_tag_results);
  $tag_search.on('keydown', function (e) {
    let $items = $tag_results.find('li[data-value]');
    let $active = $items.filter('.active');
    let index = $items.index($active);
    if (e.key == 'ArrowDown' || e.key == 'ArrowUp') {
      e.preventDefault();
      if ($tag_results.prop('hidden')) { show_tag_results(); $items = $tag_results.find('li[data-value]'); }
      index = e.key == 'ArrowDown' ? Math.min(index + 1, $items.length - 1) : Math.max(index - 1, 0);
      $items.removeClass('active');
      let item = $items.eq(index).addClass('active');
      if (item.length) { item[0].scrollIntoView({ block: 'nearest' }); }
    } else if (e.key == 'Enter') {
      e.preventDefault();
      let $choice = $active.length ? $active : $items.first();
      if ($choice.length) { select_tag($choice.attr('data-value')); }
    } else if (e.key == 'Escape') {
      $tag_results.prop('hidden', true);
    }
  });
  // Use mousedown, so that the click comes before the search box loses the focus.
  $tag_results.on('mousedown', 'li[data-value]', function (e) {
    e.preventDefault();
    select_tag($(this).attr('data-value'));
  });
  $tag_search.on('blur', function () { $tag_results.prop('hidden', true); });
  $('.pub-tag-chip').on('click', function () {
    let value = $(this).attr('data-value');
    // A second click on the selected tag shows all the publications again.
    select_tag($('.pub-tags-select').val() == value ? '*' : value);
  });
  $('.pub-tag-clear').on('click', function () { select_tag('*'); });

  // Filter publications according to hash in URL.
  function filter_publications() {
    let type = '*';
    let tag = '*';
    window.location.hash.replace('#', '').split('&').forEach(function (part) {
      if (part != '' && !isNaN(part)) {
        type = '.pubtype-' + part;
      } else if (part.substr(0, 4) == 'tag=') {
        let name = part.substr(4);
        $('.pub-tags-select option').each(function () {
          if ($(this).attr('data-tag') == name) {
            tag = $(this).val();
          }
        });
      }
    });

    $('.pub-filters-select').val(type);
    $('.pub-tags-select').val(tag);
    update_tag_search();
    let filterValue = [type, tag].filter(function (f) { return f != '*'; }).join('');
    $grid_pubs.isotope({ filter: filterValue || '*' });
  }

  /* ---------------------------------------------------------------------------
   * On window load.
   * --------------------------------------------------------------------------- */

  $(window).on('load', function() {
    if (window.location.hash) {
      // When accessing homepage from another page and `#top` hash is set, show top of page (no hash).
      if (window.location.hash == "#top") {
        window.location.hash = ""
      } else {
        // If URL contains a hash, scroll to target ID taking into account responsive offset.
        scrollToAnchor();
      }
    }

    // Initialize Scrollspy.
    let $body = $('body');
    $body.scrollspy({offset: navbar_offset });

    // Call `fixScrollspy` when window is resized.
    let resizeTimer;
    $(window).resize(function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(fixScrollspy, 200);
    });

    // Enable publication filter for publication index page.
    if ($('.pub-filters-select').length) {
      filter_publications();
      // Filter again when the hash changes (for example with the back button).
      window.addEventListener('hashchange', filter_publications, false);
    }

  });

})(jQuery);
