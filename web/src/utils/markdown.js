import { marked } from "marked";

function slugify(value = "") {
  return String(value)
    .toLowerCase()
    .trim()
    .replace(/<[^>]+>/g, "")
    .replace(/[^\w\u4e00-\u9fa5\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "") || "section";
}

function createSlugFactory() {
  const counts = new Map();
  return (text) => {
    const base = slugify(text);
    const current = counts.get(base) || 0;
    counts.set(base, current + 1);
    return current === 0 ? base : `${base}-${current + 1}`;
  };
}

function walkTokens(tokens, visitor) {
  if (!Array.isArray(tokens)) return;

  for (const token of tokens) {
    visitor(token);

    if (Array.isArray(token.tokens)) {
      walkTokens(token.tokens, visitor);
    }

    if (Array.isArray(token.items)) {
      walkTokens(token.items, visitor);
    }
  }
}

export function renderMarkdown(source = "") {
  const markdown = String(source || "");
  const tokens = marked.lexer(markdown, {
    gfm: true,
    breaks: true,
  });

  const nextSlug = createSlugFactory();
  const headings = [];

  walkTokens(tokens, (token) => {
    if (token.type === "heading") {
      const id = nextSlug(token.text);
      token.headingId = id;
      headings.push({
        id,
        text: token.text,
        depth: token.depth,
      });
    }
  });

  const renderer = new marked.Renderer();

  renderer.heading = function ({ tokens: inlineTokens, depth, text, headingId }) {
    const innerHtml = this.parser.parseInline(inlineTokens);
    return `<h${depth} id="${headingId || slugify(text)}">${innerHtml}</h${depth}>`;
  };

  renderer.link = function ({ href, title, tokens: inlineTokens }) {
    const innerHtml = this.parser.parseInline(inlineTokens);
    const isExternal = /^https?:\/\//i.test(href || "");
    const titleAttr = title ? ` title="${title}"` : "";
    const targetAttr = isExternal ? ' target="_blank" rel="noopener noreferrer"' : "";
    return `<a href="${href || "#"}"${titleAttr}${targetAttr}>${innerHtml}</a>`;
  };

  renderer.image = function ({ href, title, text }) {
    const titleAttr = title ? ` title="${title}"` : "";
    return `<img src="${href || ""}" alt="${text || ""}" loading="lazy" decoding="async"${titleAttr}>`;
  };

  const html = marked.parser(tokens, {
    gfm: true,
    breaks: true,
    renderer,
  });

  return { html, headings };
}
