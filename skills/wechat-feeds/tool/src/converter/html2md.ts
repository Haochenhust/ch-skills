import TurndownService from "turndown";
import * as cheerio from "cheerio";

const turndown = new TurndownService({
  headingStyle: "atx",
  codeBlockStyle: "fenced",
  bulletListMarker: "-",
});

turndown.remove(["script", "style", "meta", "link", "noscript"]);

// 处理微信图片（data-src 优先于 src）。如果提供了 urlToLocal 映射，写入本地相对路径。
function buildImageRule(urlToLocal?: Map<string, string>) {
  turndown.addRule("wechatImage", {
    filter: (node) => node.nodeName === "IMG",
    replacement: (_content, node) => {
      const el = node as HTMLElement;
      const src = el.getAttribute("data-src") || el.getAttribute("src") || "";
      const alt = el.getAttribute("alt") || "";
      if (!src || src.startsWith("data:")) return "";
      const target = urlToLocal?.get(src) ?? src;
      return `![${alt}](${target})\n\n`;
    },
  });
}

buildImageRule();

export interface ArticleMeta {
  title: string;
  author: string;
  date: string;
  url: string;
  digest?: string;
}

/**
 * 从文章 HTML 中提取所有图片 URL（去重、去 data:），顺序与文档出现顺序一致。
 */
export function extractImageUrls(html: string): string[] {
  const $ = cheerio.load(html);
  const urls: string[] = [];
  const seen = new Set<string>();
  $("img").each((_, el) => {
    const src = $(el).attr("data-src") || $(el).attr("src") || "";
    if (!src || src.startsWith("data:")) return;
    if (seen.has(src)) return;
    seen.add(src);
    urls.push(src);
  });
  return urls;
}

export function htmlToMarkdown(
  html: string,
  meta: ArticleMeta,
  urlToLocal?: Map<string, string>,
): string {
  // 每次重新注册图片规则，使用当前的 mapping
  buildImageRule(urlToLocal);

  const $ = cheerio.load(html);
  const content =
    $("#js_content").html() ||
    $(".rich_media_content").html() ||
    $("body").html() ||
    "";

  const markdown = turndown.turndown(content);

  const frontmatter = [
    "---",
    `title: "${meta.title.replace(/"/g, '\\"')}"`,
    `author: "${meta.author.replace(/"/g, '\\"')}"`,
    `date: ${meta.date}`,
    `url: "${meta.url}"`,
    meta.digest ? `digest: "${meta.digest.replace(/"/g, '\\"')}"` : "",
    "---",
  ]
    .filter(Boolean)
    .join("\n");

  return `${frontmatter}\n\n${markdown}\n`;
}
