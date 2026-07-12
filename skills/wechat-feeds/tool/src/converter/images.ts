import { mkdirSync, writeFileSync } from "fs";
import { join } from "path";

const WECHAT_FMT_TO_EXT: Record<string, string> = {
  jpeg: "jpeg",
  jpg: "jpeg",
  png: "png",
  gif: "gif",
  webp: "webp",
  bmp: "bmp",
  svg: "svg",
};

const CONTENT_TYPE_TO_EXT: Record<string, string> = {
  "image/jpeg": "jpeg",
  "image/jpg": "jpeg",
  "image/png": "png",
  "image/gif": "gif",
  "image/webp": "webp",
  "image/bmp": "bmp",
  "image/svg+xml": "svg",
};

function extFromUrl(url: string): string | null {
  try {
    const u = new URL(url);
    const fmt = u.searchParams.get("wx_fmt");
    if (fmt && WECHAT_FMT_TO_EXT[fmt.toLowerCase()]) {
      return WECHAT_FMT_TO_EXT[fmt.toLowerCase()];
    }
    const pathMatch = u.pathname.match(/\.([a-zA-Z0-9]+)$/);
    if (pathMatch && WECHAT_FMT_TO_EXT[pathMatch[1].toLowerCase()]) {
      return WECHAT_FMT_TO_EXT[pathMatch[1].toLowerCase()];
    }
  } catch {}
  return null;
}

function extFromContentType(ct: string | null): string | null {
  if (!ct) return null;
  const base = ct.split(";")[0].trim().toLowerCase();
  return CONTENT_TYPE_TO_EXT[base] ?? null;
}

export interface ImageDownloadResult {
  urlToLocal: Map<string, string>;
  failed: string[];
}

/**
 * 下载文章中的所有图片到 accountDir/images/articleSlug/，返回 URL → 相对路径 (相对于文章 .md) 的映射。
 * - articleSlug 用作子目录名，避免不同文章的图片冲突
 * - 失败的图片不会丢，保留原 URL（在 markdown 里）
 *
 * 默认 pull 只保存正文、图片保留原 CDN URL（不下载）。想本地化图片时，
 * 在 fetcher/pull.ts 里把这里返回的 urlToLocal 传给 htmlToMarkdown 即可。
 */
export async function downloadArticleImages(
  imageUrls: string[],
  accountDir: string,
  articleSlug: string,
): Promise<ImageDownloadResult> {
  const urlToLocal = new Map<string, string>();
  const failed: string[] = [];

  const unique = Array.from(new Set(imageUrls)).filter(
    (u) => u && !u.startsWith("data:"),
  );
  if (unique.length === 0) return { urlToLocal, failed };

  const targetDir = join(accountDir, "images", articleSlug);
  mkdirSync(targetDir, { recursive: true });

  let idx = 0;
  for (const url of unique) {
    idx++;
    const seq = String(idx).padStart(4, "0");
    try {
      const resp = await fetch(url, {
        headers: {
          Referer: "https://mp.weixin.qq.com/",
          "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
      });
      if (!resp.ok) {
        failed.push(url);
        continue;
      }
      const ext =
        extFromUrl(url) ??
        extFromContentType(resp.headers.get("content-type")) ??
        "jpg";
      const filename = `${seq}.${ext}`;
      const buf = Buffer.from(await resp.arrayBuffer());
      writeFileSync(join(targetDir, filename), buf);
      // 相对路径，相对于 accountDir 下的 .md 文件
      urlToLocal.set(url, `images/${articleSlug}/${filename}`);
    } catch {
      failed.push(url);
    }
  }

  return { urlToLocal, failed };
}
