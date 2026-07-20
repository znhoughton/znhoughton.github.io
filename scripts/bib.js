// Minimal BibTeX parser + APA-style formatter for blog citations.
//
// This is deliberately not a general-purpose BibTeX/citation engine --
// it's scoped to the entry types and fields actually used in
// blog/references.bib (article, book, incollection), which is hand-authored
// rather than exported from a reference manager, so the input is
// well-behaved by construction (single level of brace-nesting in a field
// value at most, e.g. "{Meanings}" inside a title).
//
// Citation syntax inside a post's markdown, resolved before the text is
// handed to marked:
//   [@key]              -> "(Author, Year)"          (parenthetical)
//   [@key1; @key2]       -> "(Author, Year; Author2, Year2)"
//   @key (bare, not in brackets) -> "Author (Year)"   (narrative)
// An unrecognized key renders inline as a visible "[unknown citation: key]"
// marker rather than silently vanishing or throwing, so a typo'd key is
// obvious in preview instead of shipping a broken citation.
(function (global) {
  function parseBibtex(text) {
    const entries = {};
    const entryRe = /@(\w+)\s*\{\s*([^,\s]+)\s*,([\s\S]*?)\n\}/g;
    let m;
    while ((m = entryRe.exec(text))) {
      const [, type, key, body] = m;
      const fields = {};
      const fieldRe = /(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}/g;
      let fm;
      while ((fm = fieldRe.exec(body))) {
        // "--" is BibTeX's standard range dash (page ranges, year ranges);
        // normalize to a real en dash wherever it appears, not just in pages.
        fields[fm[1].toLowerCase()] = fm[2].replace(/[{}]/g, '').replace(/--/g, '–').trim();
      }
      entries[key] = { type: type.toLowerCase(), key, fields };
    }
    return entries;
  }

  function parseAuthors(authorField) {
    if (!authorField) return [];
    return authorField.split(/\s+and\s+/).map(name => {
      const parts = name.split(',');
      const last = (parts[0] || '').trim();
      const first = (parts[1] || '').trim();
      // Split on whitespace only, so a hyphenated compound name stays one
      // token ("K.-M." or "Kai-Min"); within a token, split on "-" so its
      // own initials stay hyphen-joined too ("Kai-Min" -> "K.-M.", not
      // "K. M.").
      const initials = first
        .split(/\s+/)
        .filter(Boolean)
        .map(token => token
          .split('-')
          .filter(Boolean)
          .map(part => part.replace(/\.$/, '')[0].toUpperCase() + '.')
          .join('-'))
        .join(' ');
      return { last, initials };
    });
  }

  function apaAuthorList(authors) {
    if (authors.length === 0) return '';
    const formatted = authors.map(a => (a.initials ? `${a.last}, ${a.initials}` : a.last));
    if (formatted.length === 1) return formatted[0];
    if (formatted.length === 2) return `${formatted[0]}, & ${formatted[1]}`;
    if (formatted.length <= 20) {
      return formatted.slice(0, -1).join(', ') + ', & ' + formatted[formatted.length - 1];
    }
    // APA 7th ed.: 21+ authors -> first 19, an ellipsis (not "&"), then the
    // final author.
    return formatted.slice(0, 19).join(', ') + ', . . . ' + formatted[formatted.length - 1];
  }

  function narrativeAuthors(authors) {
    if (authors.length === 0) return '';
    if (authors.length === 1) return authors[0].last;
    if (authors.length === 2) return `${authors[0].last} & ${authors[1].last}`;
    return `${authors[0].last} et al.`;
  }

  function escapeHtml(str) {
    return String(str == null ? '' : str).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // A reference string is assembled with plain "*word*" markers for italics
  // (never full Markdown -- titles/journal names won't contain the rest of
  // Markdown's syntax), so escape everything else first, then convert just
  // that one marker into real emphasis.
  function emphasize(str) {
    return str.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  }

  function apaReference(entry) {
    const f = entry.fields;
    const authorStr = escapeHtml(apaAuthorList(parseAuthors(f.author)));
    const year = escapeHtml(f.year || 'n.d.');
    const title = escapeHtml(f.title);
    const journal = escapeHtml(f.journal);
    const booktitle = escapeHtml(f.booktitle);
    const publisher = escapeHtml(f.publisher);
    const pages = escapeHtml(f.pages || '');
    let out;
    switch (entry.type) {
      case 'article': {
        const vol = f.volume ? `, *${escapeHtml(f.volume)}*` : '';
        const num = f.number ? `(${escapeHtml(f.number)})` : '';
        const pg = pages ? `, ${pages}` : '';
        out = `${authorStr} (${year}). ${title}. *${journal}*${vol}${num}${pg}.`;
        break;
      }
      case 'book':
        out = `${authorStr} (${year}). *${title}*. ${publisher}.`;
        break;
      case 'incollection': {
        const pg = pages ? ` (pp. ${pages})` : '';
        out = `${authorStr} (${year}). ${title}. In *${booktitle}*${pg}. ${publisher}.`;
        break;
      }
      case 'online':
      case 'misc': {
        // For research notes/preprints published as a web-native series
        // rather than a traditional journal (e.g. Anthropic's Transformer
        // Circuits Thread) -- "howpublished" carries the venue name.
        const venue = f.howpublished ? ` *${escapeHtml(f.howpublished)}*.` : '';
        out = `${authorStr} (${year}). ${title}.${venue}`;
        break;
      }
      default:
        out = `${authorStr} (${year}). ${title}.`;
    }
    out = emphasize(out);
    if (f.url) {
      out += ` <a href="${escapeHtml(f.url)}" target="_blank" rel="noopener">${escapeHtml(f.url)}</a>`;
    }
    return out;
  }

  function apaInText(entry, narrative) {
    const authors = parseAuthors(entry.fields.author);
    const year = entry.fields.year || 'n.d.';
    const names = narrativeAuthors(authors);
    return narrative ? `${names} (${year})` : `${names}, ${year}`;
  }

  // Resolves citation markup in raw markdown text (before marked parses
  // it). Returns the rewritten text plus the ordered list of unique keys
  // actually cited, so the caller can build a References section from
  // only what that specific post used.
  function resolveCitations(text, entries) {
    const used = [];
    const seen = new Set();
    function lookup(key) {
      if (!seen.has(key)) { seen.add(key); used.push(key); }
      return entries[key] || null;
    }

    // Bracketed: [@key] or [@key1; @key2; ...]
    text = text.replace(/\[(@[\w-]+(?:\s*;\s*@[\w-]+)*)\]/g, (whole, inner) => {
      const keys = inner.match(/@[\w-]+/g).map(s => s.slice(1));
      const parts = keys.map(k => {
        const entry = lookup(k);
        return entry ? apaInText(entry, false) : `unknown citation: ${k}`;
      });
      return `(${parts.join('; ')})`;
    });

    // Bare narrative: @key, not preceded by "[" (already handled above)
    text = text.replace(/(^|[^\[\w@])@([\w-]+)/g, (whole, pre, key) => {
      const entry = lookup(key);
      return pre + (entry ? apaInText(entry, true) : `[unknown citation: ${key}]`);
    });

    return { text, usedKeys: used };
  }

  function renderReferences(usedKeys, entries) {
    const known = usedKeys.filter(k => entries[k]);
    if (!known.length) return '';
    const items = known
      .map(k => entries[k])
      .sort((a, b) => {
        const la = (parseAuthors(a.fields.author)[0] || {}).last || '';
        const lb = (parseAuthors(b.fields.author)[0] || {}).last || '';
        return la.localeCompare(lb);
      })
      .map(e => `<li>${apaReference(e)}</li>`)
      .join('\n');
    return `<h3>References</h3>\n<ul class="reference-list">\n${items}\n</ul>`;
  }

  global.BibCite = { parseBibtex, resolveCitations, renderReferences };
})(window);
