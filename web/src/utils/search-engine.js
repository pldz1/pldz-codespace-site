function normalize(text) {
  if (text == null) return "";
  const s = String(text).toLowerCase();
  return typeof s.normalize === "function" ? s.normalize("NFKC") : s;
}

function isSubsequence(needle, haystack) {
  if (!needle) return true;
  let i = 0,
    j = 0;

  while (i < needle.length && j < haystack.length) {
    if (needle[i] === haystack[j]) i++;
    j++;
  }

  return i === needle.length;
}

function highlightTokens(text, tokens) {
  if (!text || !tokens || !tokens.length) return text;
  let result = text;
  const uniq = Array.from(new Set(tokens.filter(Boolean)));
  uniq.sort((a, b) => b.length - a.length);
  uniq.forEach((tk) => {
    if (!tk) return;
    const escaped = tk.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`(${escaped})`, "gi");
    result = result.replace(re, "<mark>$1</mark>");
  });
  return result;
}

class SimpleSearch {
  constructor(options) {
    const defaults = { fields: [], threshold: 0.2 };
    this.opts = Object.assign({}, defaults, options || {});
    if (!Array.isArray(this.opts.fields) || this.opts.fields.length === 0) {
      throw new Error("SimpleSearch: options.fields must be a non-empty array");
    }
    this._raw = [];
    this._index = [];
  }

  load(dataArray) {
    if (!Array.isArray(dataArray)) throw new Error("SimpleSearch.load: expects an array");
    this._raw = dataArray.slice();

    this._index = dataArray.map((item, idx) => {
      const bag = this.opts.fields.map((k) => (Array.isArray(item[k]) ? item[k].join(" ") : item[k])).join(" ");

      return {
        id: idx,
        haystack: normalize(bag),
        fields: this.opts.fields.reduce((acc, k) => {
          acc[k] = normalize(Array.isArray(item[k]) ? item[k].join(" ") : item[k]);
          return acc;
        }, {}),
      };
    });

    return this;
  }

  search(query) {
    const q = normalize(query).trim();

    if (!q) return [];

    const tokens = q.split(/\s+/).filter(Boolean);
    const threshold = typeof this.opts.threshold === "number" ? this.opts.threshold : 0.2;
    const scored = this._index.map((rec, i) => {
      let score = 0;

      for (const tk of tokens) {
        if (!tk) continue;

        if (rec.haystack.includes(tk)) score += 1.0;
        else if (isSubsequence(tk, rec.haystack)) score += 0.5;
      }

      score = score / Math.max(tokens.length, 1);
      return { idx: i, score };
    });

    const filtered = scored.filter((s) => s.score >= threshold);
    filtered.sort((a, b) => b.score - a.score);

    return filtered.map((s) => ({ item: this._raw[s.idx], score: s.score }));
  }

  highlight(item, query) {
    const tokens = normalize(query).split(/\s+/).filter(Boolean);
    const out = {};
    for (const k of this.opts.fields) {
      const raw = Array.isArray(item[k]) ? item[k].join(" ") : item[k] == null ? "" : String(item[k]);
      out[k] = highlightTokens(raw, tokens);
    }
    return out;
  }
}

export default SimpleSearch;
